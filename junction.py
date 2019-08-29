import logging
import time
import hwilib
import os.path

from pprint import pprint
from hwilib.serializations import PSBT

from utils import write_json_file, read_json_file, RPC, JSONRPCException, sat_to_btc, btc_to_sat, get_settings, JunctionError

logger = logging.getLogger(__name__)

class MultisigWallet:

    def __init__(self, name, m, n, signers, psbt, address_index):
        # Name of the wallet
        self.name = name
        # Signers required for bitcoin tx
        self.m = m
        # Total signers
        self.n = n
        # Dictionary
        self.signers = signers
        # Hex string
        self.psbt = psbt
        # Depth in HD derivation
        self.address_index = address_index
        # RPC connection to corresponding watch-only wallet in Bitcoin Core
        self.wallet_rpc = RPC(name)

    def ready(self):
        '''All signers present, ready to create PSBT'''
        return len(self.signers) == self.n

    def filename(self):
        '''Relative path to wallet file'''
        return f"wallets/{self.name}.json"

    @classmethod
    def create(cls, name, m, n):
        '''Create new instance of this class.
        Creates wallet file and watch-only Bitcoin Core wallet as side-effects'''
        # Sanity check
        if m > n:
            raise JunctionError(f"\"m\" ({m}) must be no larger than \"n\" ({n})")

        # MultisigWallet instance
        wallet = cls(name, m, n, [], None, 0)

        # Never overwrite existing wallet files
        filename = wallet.filename()
        if os.path.exists(filename):
            raise JunctionError(f'"{filename}" already exists')

        # Create a watch-only Bitcoin Core wallet
        wallet.ensure_watchonly()

        # Save a copy of wallet to disk
        wallet.save()

        # Return instance
        return wallet

    @classmethod
    def open(cls, wallet_name):
        '''Initialize this class from an existing wallet file'''
        file_name = f'wallets/{wallet_name}.json'
        wallet_dict = read_json_file(file_name)
        wallet = cls.from_dict(wallet_dict)
        logger.info(f"Opened wallet from {file_name}")
        return wallet

    def save(self):
        '''Save wallet file to disk'''
        filename = self.filename()
        data = self.to_dict()  
        write_json_file(data, filename)
        logger.info(f"Saved wallet to {filename}")

    @classmethod
    def from_dict(cls, d):
        '''Create class instance from dictionary'''
        if d["psbt"]:
            psbt = hwilib.serializations.PSBT()
            psbt.deserialize(d["psbt"])
            d["psbt"] = psbt
        return cls(**d)
        
    def to_dict(self):
        '''Represent instance as a dictionary'''
        return {
            "name": self.name,
            "m": self.m,
            "n": self.n,
            "signers": self.signers,
            "psbt": self.psbt.serialize() if self.psbt else "",
            "address_index": self.address_index,
        }

    def add_signer(self, name, fingerprint, xpub, deriv_path):
        '''Add a signer to multisig wallet'''
        # FIXME: deriv_path not used ...
        if self.ready():
            raise JunctionError(f'Already have {len(self.signers)} of {self.n} required signers')

        # Check if name used before
        if name in [signer["name"] for signer in self.signers]:
            raise JunctionError(f'Name "{name}" already taken')

        # Check if fingerprint used before
        if fingerprint in [signer["fingerprint"] for signer in self.signers]:
            raise JunctionError(f'Fingerprint "{fingerprint}" already used')

        self.signers.append({"name": name, "fingerprint": fingerprint, "xpub": xpub})
        logger.info(f"Registered signer \"{name}\"")

        # Export next chunk watch-only addresses to Bitcoin Core if we're done adding signers
        if self.ready():
            self.export_watchonly()

        self.save()

    def remove_signer(signer_name):
        '''Remove signer from multisig wallet'''
        raise NotImplementedError()

    def descriptor(self):
        '''Descriptor for shared multisig addresses'''
        # TODO: consider using HWI's Descriptor class
        path_prefix = "/44h/1h/0h"
        # TODO: add change parameter and inject here
        path_suffix = "/0/*"
        xpubs = [f'[{signer["fingerprint"]}{path_prefix}]{signer["xpub"]}{path_suffix}' 
                for signer in self.signers]
        xpubs = ",".join(xpubs)
        descriptor = f"sh(multi({self.m},{xpubs}))"
        logger.info(f"Exporting descriptor: {descriptor}")
        # validates and appends checksum
        r = self.wallet_rpc.getdescriptorinfo(descriptor)
        return r['descriptor']

    def address(self):
        '''Derive next BIP67-compliant receiving address'''
        if not self.ready():
            raise JunctionError(f'{self.n} signers required, {len(self.signers)} registered')
        address = self.wallet_rpc.deriveaddresses(
            self.descriptor(), 
            [self.address_index, self.address_index + 1])[0]
        self.address_index += 1

        # Hackily skip BIP67 (sorted multisig pubkeys) violations
        # (ColdCard demands BIP67 compliance, descriptor language doesn't support)
        ai = self.wallet_rpc.getaddressinfo(address)
        if ai['pubkeys'] != sorted(ai['pubkeys']):
            return self.address()
            
        self.save()
        return address

    def ensure_watchonly(self):
        # Create watch-only Bitcoin Core wallet
        watch_only_name = self.watchonly_name()
        default_wallet_rpc = RPC()
        bitcoin_wallets = default_wallet_rpc.listwallets()
        if watch_only_name not in bitcoin_wallets:
            try:
                default_wallet_rpc.loadwallet(watch_only_name)
                logger.info(f"Loaded watch-only Bitcoin Core wallet \"{watch_only_name}\"")
            except JSONRPCException as e:
                try:
                    default_wallet_rpc.createwallet(watch_only_name, True)
                    logger.info(f"Created watch-only Bitcoin Core wallet \"{watch_only_name}\"")
                except JSONRPCException as e:
                    raise JunctionError("Couldn't establish watch-only Bitcoin Core wallet")

    def watchonly_name(self):
        # maybe add a "junction_" prefix or something?
        return self.name

    def export_watchonly(self):
        '''Export addresses to Bitcoin Core watch-only wallet'''
        logger.info("Starting watch-only export")
        address_chunk = get_settings()['address_chunk']
        self.wallet_rpc.importmulti([{
            "desc": self.descriptor(),
            # 24 hours just in case
            "timestamp": int(time.time()) - 60*60*24,
            "range": [self.address_index, address_chunk],
            "watchonly": True,
            # Bitcoin Core cannot import P2SH/P2WSH: https://bitcoin.stackexchange.com/a/89118/85335
            "keypool": False,
            "internal": False,
        }])
        logger.info("Finished watch-only export")

    def create_psbt(self, recipient, satoshis):
        '''Create a new PSBT paying single recipient'''
        if self.psbt:
            raise JunctionError('PSBT already present')
        change_address = self.address()
        raw_psbt = self.wallet_rpc.walletcreatefundedpsbt(
            # let Bitcoin Core choose inputs
            [],
            # Outputs
            [{recipient: sat_to_btc(satoshis)}],
            # Locktime
            0, 
            {
                # Include watch-only outputs
                "includeWatching": True,
                # Provide change address b/c Core can't generate it
                "changeAddress": change_address,
            },
            # Include BIP32 derivation paths in the PSBT
            True,
        )['psbt']
        # Serialize and save
        self.psbt = hwilib.serializations.PSBT()
        self.psbt.deserialize(raw_psbt)
        self.save()

    def remove_psbt(self):
        self.psbt = None

    def decode_psbt(self):
        '''Fetch Bitcoin Core psbt deserialization if it exists'''
        if self.psbt:
            return self.wallet_rpc.decodepsbt(self.psbt.serialize())
        else:
            return None

    def signing_complete(self):
        '''Check that we have m signatures'''
        return self.m == len(self.psbt.inputs[0].partial_sigs)

    def broadcast(self):
        '''Finalize and broadcast psbt to network'''
        psbt_hex = self.psbt.serialize()
        tx_hex = self.wallet_rpc.finalizepsbt(psbt_hex)["hex"]
        return self.wallet_rpc.sendrawtransaction(tx_hex)
    
    def balances(self):
        '''(unconfirmed, confirmed) balances tuple'''
        # try to use new getbalances rpc (available in bitcoin core master branch)
        try:
            balances = self.wallet_rpc.getbalances()
            if 'watchonly' in balances:
                watchonly = balances['watchonly']
                return watchonly['untrusted_pending'], watchonly['trusted']
            else:
                return 0, 0
        # fall back to getbalance and no unconfirmed balance
        except:
            unconfirmed_balance = 0
            confirmed_balance = 0
            unspent = self.wallet_rpc.listunspent(0, 9999999, [], True)
            for u in unspent:
                if u['confirmations'] > 0:
                    confirmed_balance += u['amount']
                else:
                    unconfirmed_balance += u['amount']
            return unconfirmed_balance, confirmed_balance
