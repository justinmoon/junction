import logging
import time
import hwilib
import os.path

from pprint import pprint
from hwilib.serializations import PSBT

from utils import RPC, JSONRPCException, sat_to_btc, btc_to_sat, JunctionError, read_cookie, derive_child_sec_from_xpub
from disk import write_json_file, read_json_file, full_path

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
        if extras:
            base['rpc_error'] = self.default_rpc.error()
        return base

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def read_cookie(self):
        user, password = read_cookie(None, self.network)
        if user and password:
            self.user, self.password, self.cookie_auth = user, password, True
    
class MultisigWallet:

    def __init__(self, *, name, m, n, signers, psbts, receiving_address_index, 
                 change_address_index, node, network, script_type, wallet_type):
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
        # Depth in HD derivation
        self.change_address_index = change_address_index
        # bitcoin node this wallet is attached to
        self.node = node
        # "mainnet", "testnet" or "regtest"
        self.network = network
        # "wrapped" or "native"
        self.script_type = script_type
        # "single" or "multi"
        self.wallet_type = wallet_type

    ### Helper methods

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
        if n > 20:
            raise JunctionError(f"\"n\" ({n}) cannot exceed 20")

        # FIXME: make sure that no RPC wallet with this name exists
        # Perhaps we should be connecting to a node, first

        # MultisigWallet instance
        wallet = cls(name=name, m=m, n=n, signers=[], psbts=[], receiving_address_index=0,
                     change_address_index=0, node=node, network=network, script_type=script_type,
                     wallet_type=wallet_type)

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

        # From here we can assume that either Bitcoin Core wallet is loaded or we can't connect to node
        try:
            wallet.ensure_watchonly()
        except Exception as e:
            logger.info('Could not load Bitcoin Core "{}" wallet: {}'.format(wallet.name, str(e)))
        
        logger.info(f"Opened wallet from {relative_path}")
        return wallet

    def save(self):
        '''Save wallet file to disk'''
        data = self.to_dict()  
        relative_path = self.wallet_file_path()
        write_json_file(data, relative_path)
        logger.info(f"Saved wallet to {relative_path}")

    ### Serialization

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
        base = {
            "name": self.name,
            "m": self.m,
            "n": self.n,
            "signers": signers,
            "psbts": psbts,
            "receiving_address_index": self.receiving_address_index,
            "change_address_index": self.change_address_index,
            "node": self.node.to_dict(extras),
            "network": self.network,
            "wallet_type": self.wallet_type,
            "script_type": self.script_type,
        }
        # FIXME: this sucks, but we need a way to serialize for API
        if extras:
            # FIXME: hack so that rpc calls don't blow up when we don't have a node available ...
            base['ready'] = self.ready()
            if self.node.default_rpc.error():
                base['balances'] = {
                    # FIXME: this is bad. Shouldn't present incorrect balances, ever.
                    'confirmed': 'unavailable',
                    'unconfirmed': 'unavailable',
                }
                base['psbts'] = []
                base['coins'] = []
                base['history'] = []
                base['synced'] = None        
            else:
                unconfirmed, confirmed = self.balances()
                base['balances'] = {
                    'confirmed': confirmed,
                    'unconfirmed': unconfirmed,
                }
                base['psbts'] = [self.decode_psbt(psbt) for psbt in self.psbts]
                base['coins'] = self.coins()
                base['history'] = self.history()
                base['synced'] = self.synced()
        return base

    ### Watch-only Bitcoin Core wallets

    def watchonly_name(self):
        """Name of associated Bitcoin Core watch-only wallet"""
        return f"{self.name}"

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

    ### Signers

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
        
        # sort lexigraphically by xpubs
        signers = self.signers + [signer]
        self.signers = sorted(signers, key=lambda signer: signer.xpub)
        logger.info(f"Registered signer \"{name}\"")

        self.save()

    def remove_signer(signer_name):
        '''Remove signer from multisig wallet'''
        raise NotImplementedError()

    ### Addresses

    def account_derivation_path(self):
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

    def descriptor(self, change, index):
        # For multisig, order the xpubs lexigraphically by derived SEC pubkeys that will go in bitcoin script (BIP67)
        if self.wallet_type == 'multi':
            path = f"./{int(change)}/{index}"
            secs_and_signers = [(derive_child_sec_from_xpub(signer.xpub, path), signer) 
                                for signer in self.signers]
            sorted_secs_and_signers = sorted(secs_and_signers, key=lambda item: item[0])
            signers = [sec_and_signer[1] for sec_and_signer in sorted_secs_and_signers]
        else:
            signers = self.signers

        # Build the descriptor according to script type
        parts_list = [f'[{signer.fingerprint}{signer.derivation_path[1:]}]{signer.xpub}/{int(change)}/{index}' 
                for signer in signers]
        parts_str = ",".join(parts_list)
        if self.script_type == 'native' and self.wallet_type == 'multi':
            descriptor = f"wsh(multi({self.m},{parts_str}))"
        elif self.script_type == 'native' and self.wallet_type == 'single':
            descriptor = f"wpkh({parts_str})"
        elif self.script_type == 'wrapped' and self.wallet_type == 'multi':
            descriptor = f"sh(wsh(multi({self.m},{parts_str})))"
        elif self.script_type == 'wrapped' and self.wallet_type == 'single':
            descriptor = f"sh(wpkh({parts_str}))"
        else:
            raise Exception('Cannot construct descriptor')
        
        # validates and appends checksum
        # FIXME: do this here
        r = self.node.wallet_rpc.getdescriptorinfo(descriptor)
        return r['descriptor']

    def derive_receiving_address(self):
        '''Derive next change address, sync if we need to and save new address indices'''
        # Define params for readability sake
        change = False
        address_index = self.receiving_address_index

        # Get the address
        address = self.derive_address(change, address_index)
        
        # Update state, save and return address
        self.receiving_address_index += 1
        self.save()
        return address

    def derive_change_address(self):
        '''Derive next change address, sync if we need to and save new address indices'''
        # Define params for readability sake
        change = True
        address_index = self.change_address_index

        # Get the address
        address = self.derive_address(change, address_index)
        
        # Update state, save and return address
        self.change_address_index += 1
        self.save()
        return address

    def derive_address(self, change, index):
        '''Helper for deriving address at specified change/index position'''
        # Can't derive addresses if we don't have enough signers
        if not self.ready():
            raise JunctionError(f'{self.n} signers required, {len(self.signers)} registered')
        
        # Tell Bitcoin Core to watch this address
        descriptor = self.watch_address(change, index)

        # Get the address from Bitcoin Core
        address = self.node.wallet_rpc.deriveaddresses(descriptor)[0]

        # Make sure we got a watch-only address
        address_info = self.node.wallet_rpc.getaddressinfo(address)
        assert address_info['iswatchonly'] is True, 'Bitcoin Core gave us non-watch-only address'

        # Make sure multisig pubkeys are sorted (FIXME: raise or recurse?)
        if self.wallet_type == 'multi':
            if self.script_type == 'wrapped':
                pubkeys = address_info['embedded']['pubkeys']
            else:
                pubkeys = address_info['pubkeys']
            assert sorted('pubkeys'), 'Derived address with unsorted pubkeys'
            
        return address

    def watch_address(self, change, index):
        '''Tell Bitcoin Core to watch address at change / index'''
        descriptor = self.descriptor(change, index)
        response = self.node.wallet_rpc.importmulti([{
            "desc": descriptor,
            # rescan from thie timestamp ('now' means no rescan)
            "timestamp": 'now',
            # Treat as a watch-only address
            "watchonly": True,
            # Don't import into keypool. Bitcoin Core can't yet import multisig addresses.
            # Using same behavior for single & multisig for simplicity sake
            "keypool": False,
            # Is it change?
            "internal": change,
        }])
        assert all([item['success'] for item in response]), 'Address export failed'

        # slightly janky, but helps in derive_address
        return descriptor

    def watching_address(self, change, index):
        '''Check if Bitcoin Core is already watching this address'''
        # Grab descriptor, derive address, see if watch-only RPC tags it as "iswatchonly"
        descriptor = self.descriptor(change, index)
        address = self.node.default_rpc.deriveaddresses(descriptor)[0]
        address_info = self.node.wallet_rpc.getaddressinfo(address)
        return address_info.get('iswatchonly', False)
    
    def synced(self):
        '''Ballpark guess whether we're synced with Bitcoin Core'''
        checks = []
        if self.change_address_index != 0:
            checks.append(self.watching_address(True, 0))
            checks.append(self.watching_address(True, self.change_address_index-1))
        if self.receiving_address_index != 0:
            checks.append(self.watching_address(False, 0))
            checks.append(self.watching_address(False, self.receiving_address_index-1))
        return all(checks)

    def sync(self):
        '''Export every address that Bitcoin Core doesn't know about'''
        # Sync change addresses
        change = True
        for index in range(0, self.change_address_index):
            watching = self.watching_address(change, index)
            if not watching:
                self.watch_address(change, index)

        # Sync receiving addresses
        change = False
        for index in range(0, self.receiving_address_index):
            watching = self.watching_address(change, index)
            if not watching:
                self.watch_address(change, index)

    ### Transactions

    def create_psbt(self, outputs, subtract_fees=None):
        '''Create a new PSBT paying single recipient'''
        change_address = self.derive_change_address()
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
                "subtractFeeFromOutputs": subtract_fees if subtract_fees is not None else [],
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
    
    ### Wallet history

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