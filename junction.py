import logging
import time
import hwilib
import os.path

from pprint import pprint
from hwilib.serializations import PSBT

from utils import RPC, JSONRPCException, sat_to_btc, btc_to_sat, JunctionError, read_cookie
from disk import write_json_file, read_json_file, get_settings, full_path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ADDRESS_CHUNK = 100

class HardwareSigner:

    def __init__(self, *, name, xpub, fingerprint, type, derivation_path):
        self.name = name
        self.xpub = xpub
        self.fingerprint = fingerprint
        self.type = type
        self.derivation_path = derivation_path

    def to_dict(self):
        return {
            'name': self.name,
            'xpub': self.xpub,
            'fingerprint': self.fingerprint,
            'type': self.type,
            'derivation_path': self.derivation_path,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

class Node:

    def __init__(self, *, host, port, user, password, wallet_name, network):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.wallet_name = wallet_name
        self.network = network

        # keep track of whether cookie auth was used, so we don't accidentally save temporary passwords
        # is self.user == "__cookie__" a sufficient check? Then we could kill this self.auth_cookie parameter
        self.cookie_auth = self.user == None and self.password == None    
        if self.cookie_auth:
            self.read_cookie()

        # RPC connections
        base_uri = "http://{user}:{password}@{host}:{port}/wallet/".format(
            host=host, port=port, user=user, password=password
        )

        if wallet_name:
            self.wallet_rpc = RPC(base_uri + wallet_name, timeout=180)
        self.default_rpc = RPC(base_uri, timeout=180)
    
    def to_dict(self, extras):
        base = {
            'host': self.host,
            'port': str(self.port),
            'user': self.user if not self.cookie_auth else None,
            'password': self.password if not self.cookie_auth else None,
            'network': self.network,
            'wallet_name': self.wallet_name,
        }
        # FIXME
        if extras and hasattr(self, 'running'):
            base['running'] = self.running
        return base

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def read_cookie(self):
        self.user, self.password = read_cookie(None, self.network)
    
class MultisigWallet:

    def __init__(self, *, name, m, n, signers, psbts, receiving_address_index, receiving_export_index, 
                 change_address_index, change_export_index, node, network, script_type, wallet_type):
        # Name of the wallet
        self.name = name
        # Signers required for bitcoin tx
        self.m = m
        # Total signers
        self.n = n
        # Dictionary
        self.signers = signers
        # Hex string
        self.psbts = psbts
        # Depth in HD derivation
        self.receiving_address_index = receiving_address_index
        # Highest exported address index
        self.receiving_export_index = receiving_export_index
        # Depth in HD derivation
        self.change_address_index = change_address_index
        # Highest exported address index
        self.change_export_index = change_export_index
        # bitcoin node this wallet is attached to
        self.node = node
        # "mainnet", "testnet" or "regtest"
        self.network = network
        # "wrapped" or "native"
        self.script_type = script_type
        # "single" or "multi"
        self.wallet_type = wallet_type

    def ready(self):
        '''All signers present, ready to create PSBT'''
        return len(self.signers) == self.n

    def wallet_file_path(self):
        '''Relative path to wallet file within datadir'''
        return f'wallets/{self.name}.json'

    @classmethod
    def create(cls, *, name, m, n, node, network, script_type, wallet_type):
        '''Creates class instance, wallet file, and watch-only Bitcoin Core wallet'''
        # Sanity checks
        if m > n:
            raise JunctionError(f"\"m\" ({m}) must be no larger than \"n\" ({n})")
        if m < 1:
            raise JunctionError(f"\"m\" ({m}) must be larger than 0")
        if n > 5:
            raise JunctionError(f"\"n\" ({n}) cannot exceed 5")

        # FIXME: make sure that no RPC wallet with this name exists
        # Perhaps we should be connecting to a node, first

        # MultisigWallet instance
        wallet = cls(name=name, m=m, n=n, signers=[], psbts=[], receiving_address_index=0, receiving_export_index=0,
                     change_address_index=0, change_export_index=0, node=node, network=network, 
                     script_type=script_type, wallet_type=wallet_type)

        # Never overwrite existing wallet files
        # FIXME: full_path probably shouldn't appear in this file?
        wallet_file_path = full_path(f'wallets/{name}.json')
        if os.path.exists(wallet_file_path):
            raise JunctionError(f'"{wallet_file_path}" wallet file already exists')

        # Create a watch-only Bitcoin Core wallet
        wallet.ensure_watchonly()

        # Save a copy of wallet to disk
        wallet.save()

        # Return instance
        return wallet

    @classmethod
    def open(cls, wallet_name, ensure_watchonly=True):
        '''Initialize this class from an existing wallet file'''
        relative_path = f'wallets/{wallet_name}.json'
        wallet_dict = read_json_file(relative_path)
        wallet = cls.from_dict(wallet_dict)
        # FIXME: this probably isn't right. people should be able to use wallet w/o bitcoind running
        # decorating methods that require bitcoind might be a better approach
        if ensure_watchonly:
            wallet.ensure_watchonly()
        logger.info(f"Opened wallet from {relative_path}")
        return wallet

    def save(self):
        '''Save wallet file to disk'''
        data = self.to_dict()  
        relative_path = self.wallet_file_path()
        write_json_file(data, relative_path)
        logger.info(f"Saved wallet to {relative_path}")

    @classmethod
    def from_dict(cls, d):
        '''Create class instance from dictionary'''
        psbts = []
        for raw_psbt in d['psbts']:
            psbt = hwilib.serializations.PSBT()
            psbt.deserialize(raw_psbt)
            psbts.append(psbt)
        d['psbts'] = psbts
        d['signers'] = [HardwareSigner.from_dict(signer) for signer in d['signers']]
        d['node'] = Node.from_dict(d['node'])
        return cls(**d)
        
    def to_dict(self, extras=False):
        '''Represent instance as a dictionary'''
        psbts = []
        for psbt in self.psbts:
            psbt.tx.rehash()
            serialized = psbt.serialize()
            psbts.append(serialized)
        # sort signers lexigraphically by their xpub, this way any permutation of signers
        # with same keys will always generate the same wallet
        signers = [signer.to_dict() for signer in self.signers]
        ordered_signers = sorted(signers, key=lambda signer: signer['xpub'])
        base = {
            "name": self.name,
            "m": self.m,
            "n": self.n,
            "signers": ordered_signers,
            "psbts": psbts,
            "receiving_address_index": self.receiving_address_index,
            "receiving_export_index": self.receiving_export_index,
            "change_address_index": self.change_address_index,
            "change_export_index": self.change_export_index,
            "node": self.node.to_dict(extras),
            "network": self.network,
            "wallet_type": self.wallet_type,
            "script_type": self.script_type,
        }
        # FIXME: this sucks, but we need a way to serialize for API
        if extras:
            # TODO: consider adding some metadata to psbt -- e.g. # signatures remaining
            base['ready'] = self.ready()
            unconfirmed, confirmed = self.balances()
            base['balances'] = {
                'confirmed': confirmed,
                'unconfirmed': unconfirmed,
            }
            base['psbts'] = [self.decode_psbt(psbt) for psbt in self.psbts]
            base['coins'] = self.coins()
            base['history'] = self.history()
        return base

    def add_signer(self, *, name, fingerprint, xpub, type, derivation_path):
        '''Add a signer to multisig wallet'''
        if self.ready():
            raise JunctionError(f'Already have {len(self.signers)} of {self.n} required signers')

        # Check if name used before
        if name in [signer.name for signer in self.signers]:
            raise JunctionError(f'Name "{name}" already taken')

        # Check if fingerprint used before
        if fingerprint in [signer.fingerprint for signer in self.signers]:
            raise JunctionError(f'Fingerprint "{fingerprint}" already used')

        signer = HardwareSigner(name=name, fingerprint=fingerprint, xpub=xpub,
                type=type, derivation_path=derivation_path)
        self.signers.append(signer)
        logger.info(f"Registered signer \"{name}\"")

        # Export first chunk watch-only addresses to Bitcoin Core if we're done adding signers
        if self.ready():
            self.export_watchonly(change=True)
            self.export_watchonly(change=False)

        self.save()

    def remove_signer(signer_name):
        '''Remove signer from multisig wallet'''
        raise NotImplementedError()

    def descriptor(self, change):
        '''Descriptor for shared multisig addresses'''
        # TODO: signer.prefix would be better than `{signer.fingerprint}{signer.derivation_path[1:]}`
        # this would combine fingerprint & derivation path into one field. nice ...
        # then we could have signer.fingerprint() grab just the fingerprint ...
        xpubs = [f'[{signer.fingerprint}{signer.derivation_path[1:]}]{signer.xpub}/{int(change)}/*' 
                for signer in self.signers]
        xpubs = ",".join(xpubs)
        if self.script_type == 'native' and self.wallet_type == 'multi':
            descriptor = f"wsh(multi({self.m},{xpubs}))"
        elif self.script_type == 'native' and self.wallet_type == 'single':
            descriptor = f"wpkh({xpubs})"
        elif self.script_type == 'wrapped' and self.wallet_type == 'multi':
            descriptor = f"sh(wsh(multi({self.m},{xpubs})))"
        elif self.script_type == 'wrapped' and self.wallet_type == 'single':
            descriptor = f"sh(wpkh({xpubs}))"
        else:
            raise Exception('Cannot construct descriptor')
        logger.info(f"Exporting descriptor: {descriptor}")
        # validates and appends checksum
        r = self.node.wallet_rpc.getdescriptorinfo(descriptor)
        return r['descriptor']

    def address(self, change):
        '''Derive next BIP67-compliant receiving address'''
        address_index = self.change_address_index if change else self.receiving_address_index
        export_index = self.change_export_index if change else self.receiving_export_index
        if not self.ready():
            raise JunctionError(f'{self.n} signers required, {len(self.signers)} registered')
        if address_index > export_index:
            self.export_watchonly(change=change)
        address = self.node.wallet_rpc.deriveaddresses(
            self.descriptor(change),
            [address_index, address_index + 1])[0]
        
        # increment indices
        if change:
            self.change_address_index += 1
        else:
            self.receiving_address_index += 1
        
        # Make sure we got a watch-only address
        ai = self.node.wallet_rpc.getaddressinfo(address)
        assert ai['iswatchonly'] is True, 'Bitcoin Core gave us non-watch-only address'

        # Hackily skip BIP67 (sorted multisig pubkeys) violations
        # (ColdCard demands BIP67 compliance, descriptor language support not released yet)
        if self.wallet_type == 'multi':
            if self.script_type == 'wrapped':
                if ai['embedded']['pubkeys'] != sorted(ai['embedded']['pubkeys']):
                    return self.address(change)
            else:
                if ai['pubkeys'] != sorted(ai['pubkeys']):
                    return self.address(change)
            
        self.save()
        return address

    def account_derivation_path(self):
        # FIXME: testnet ...
        coin_type = int(self.network != 'mainnet')
        if self.script_type == 'native' and self.wallet_type == 'multi':
            return f"m/48'/{coin_type}'/0'/2'" 
        elif self.script_type == 'native' and self.wallet_type == 'single':
            return f"m/48'/{coin_type}'/0'"
        elif self.script_type == 'wrapped' and self.wallet_type == 'multi':
            return f"m/48'/{coin_type}'/0'/1'"
        elif self.script_type == 'wrapped' and self.wallet_type == 'single':
            return f"m/49'/{coin_type}'/0'"
        else:
            raise Exception('No derivation paths for this wallet type')

    def ensure_watchonly(self):
        # TODO: move to Node class
        # Create watch-only Bitcoin Core wallet
        watch_only_name = self.watchonly_name()
        bitcoin_wallets = self.node.default_rpc.listwallets()
        if watch_only_name not in bitcoin_wallets:
            try:
                self.node.default_rpc.loadwallet(watch_only_name)
                logger.info(f"Loaded watch-only Bitcoin Core wallet \"{watch_only_name}\"")
            except JSONRPCException as e:
                try:
                    # FIXME: if wallet is "ready" here, we also need an export ...
                    self.node.default_rpc.createwallet(watch_only_name, True)
                    logger.info(f"Created watch-only Bitcoin Core wallet \"{watch_only_name}\"")
                except JSONRPCException as e:
                    raise JunctionError("Couldn't establish watch-only Bitcoin Core wallet")

    def watchonly_name(self):
        """Name of associated Bitcoin Core watch-only wallet"""
        return f"{self.name}"

    def export_watchonly(self, *, change):
        '''Export addresses to Bitcoin Core watch-only wallet'''
        # it would be really nice if we could sanity-check against getwalletinfo here ...
        logger.info("Starting watch-only export")
        old_export_index = self.change_export_index if change else self.receiving_export_index
        new_export_index = old_export_index + ADDRESS_CHUNK
        self.node.wallet_rpc.importmulti([{
            "desc": self.descriptor(change),
            # 24 hours just in case
            "timestamp": 'now',
            # FIXME: is this inclusive? if we we're overlapping 1 ever time ...
            "range": [old_export_index, new_export_index],
            "watchonly": True,
            # Bitcoin Core cannot import P2SH/P2WSH: https://bitcoin.stackexchange.com/a/89118/85335
            "keypool": False,
            "internal": False,
        }])
        if change:
            self.change_export_index = new_export_index
        else:
            self.receiving_export_index = new_export_index
        self.save()
        logger.info("Finished watch-only export")

    def create_psbt(self, outputs):
        '''Create a new PSBT paying single recipient'''
        change_address = self.address(True)
        raw_psbt = self.node.wallet_rpc.walletcreatefundedpsbt(
            # let Bitcoin Core choose inputs
            [],
            # Outputs
            outputs,
            # Locktime
            0, 
            {
                # Include watch-only outputs
                "includeWatching": True,
                # Provide change address b/c Core can't generate it
                "changeAddress": change_address,
                # Reserve UTXOs we're spending
                "lockUnspents": True,
            },
            # Include BIP32 derivation paths in the PSBT
            True,
        )['psbt']
        # Serialize and save
        psbt = hwilib.serializations.PSBT()
        psbt.deserialize(raw_psbt)
        self.psbts.append(psbt)
        self.save()

    def remove_psbt(self, index):
        # TODO: unlock input utxos
        del self.psbts[index]
        self.save()

    def update_psbt(self, psbt, index):
        # FIXME: make sure this is the same psbt
        # does HWI PSBT class expose any "update" functionality?
        self.psbts[index] = psbt
        self.save()

    def decode_psbt(self, psbt):
        '''Fetch Bitcoin Core psbt deserialization if it exists'''
        return self.node.wallet_rpc.decodepsbt(psbt.serialize())
            
    def broadcast(self, index):
        '''Finalize and broadcast psbt to network'''
        psbt = self.psbts[index]
        psbt_hex = psbt.serialize()
        tx_hex = self.node.wallet_rpc.finalizepsbt(psbt_hex)["hex"]
        txid = self.node.wallet_rpc.sendrawtransaction(tx_hex)
        # FIXME: can we be sure that tx broadcast succeeded here, that we won't need psbt anymore?
        self.remove_psbt(index)
        return txid
    
    def balances(self):
        '''(unconfirmed, confirmed) balances tuple'''
        # try to use new getbalances rpc (available in bitcoin core master branch)
        try:
            balances = self.node.wallet_rpc.getbalances()
            if 'watchonly' in balances:
                watchonly = balances['watchonly']
                return watchonly['untrusted_pending'], watchonly['trusted']
            else:
                return 0, 0
        # fall back to counting ourselves
        except:
            unconfirmed_balance = 0
            confirmed_balance = 0
            unspent = self.coins()
            for u in unspent:
                if u['confirmations'] > 0:
                    confirmed_balance += u['amount']
                else:
                    unconfirmed_balance += u['amount']
            return unconfirmed_balance, confirmed_balance
    
    def coins(self):
        unlocked_unspents = self.node.wallet_rpc.listunspent(0, 9999999, [], True)
        locked_outpoints = self.node.wallet_rpc.listlockunspent()
        locked_unspents = []
        for outpoint in locked_outpoints:
            _unspent = self.node.wallet_rpc.gettransaction(outpoint['txid'], True)
            for details in _unspent['details']:
                unspent = {}
                unspent['txid'] = _unspent['txid']
                unspent['confirmations'] = _unspent['confirmations']
                unspent['address'] = details['address']
                unspent['vout'] = details['vout']
                unspent['amount'] = details['amount']
                locked_unspents.append(unspent)
        return unlocked_unspents + locked_unspents

    def history(self):
        # TODO: paginate
        return self.node.wallet_rpc.listtransactions("*", 100, 0, True)
    
    def addresses(self):
        pass