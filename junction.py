import logging
import os.path
import hwilib

from rpc import RPC, JSONRPCException
from pprint import pprint
from hwilib.serializations import PSBT

from utils import write_json_file, read_json_file

logger = logging.getLogger(__name__)

# FIXME
if os.path.isfile('settings.json'):
    settings = read_json_file("settings.json")
else:
    settings = read_json_file('settings.json.ex')

bitcoin_uri = "http://{username}:{password}@{host}:{port}"
bitcoin_rpc = RPC(bitcoin_uri.format(**settings["rpc"]))


class JunctionError(Exception):
    pass


class MultiSig:

    wallet_template = "http://{username}:{password}@{host}:{port}/wallet/{name}"

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
        wallet_uri = self.wallet_template.format(**settings["rpc"], name=self.watchonly_name())
        self.wallet_rpc = RPC(wallet_uri)

    def ready(self):
        return len(self.signers) == self.n

    def filename(self):
        return f"wallets/{self.name}.json"

    @classmethod
    def create(cls, name, m, n):
        # sanity check
        if m > n:
            raise JunctionError(f"\"m\" ({m}) must be no larger than \"n\" ({n})")

        # MultiSig instance
        multisig = cls(name, m, n, [], None, 0)

        # Never overwrite existing wallet files
        filename = multisig.filename()
        if os.path.exists(filename):
            raise JunctionError(f'"{filename}" already exists')

        # create a watch-only Bitcoin Core wallet
        multisig.create_watchonly()

        # Save a copy of wallet to disk
        multisig.save()

        # Return instance
        return multisig

    @classmethod
    def open(cls, wallet_name):
        file_name = f'wallets/{wallet_name}.json'
        multisig_dict = read_json_file(file_name)
        multisig = cls.from_dict(multisig_dict)
        logger.info(f"Opened wallet from {file_name}")
        return multisig

    def save(self):
        filename = self.filename()
        # if this line broke inside json.dump, the json file would be emptyed :eek:
        data = self.to_dict()  
        write_json_file(data, filename)
        logger.info(f"Saved wallet to {filename}")

    @classmethod
    def from_dict(cls, d):
        if d["psbt"]:
            psbt = hwilib.serializations.PSBT()
            psbt.deserialize(d["psbt"])
            d["psbt"] = psbt
        return cls(**d)
        
    def to_dict(self):
        return {
            "name": self.name,
            "m": self.m,
            "n": self.n,
            "signers": self.signers,
            "psbt": self.psbt.serialize() if self.psbt else "",
            "address_index": self.address_index,
        }

    def add_signer(self, name, fingerprint, xpub, deriv_path):
        # FIXME: deriv_path not used ...
        if self.ready():
            raise JunctionError(f'Already have {len(self.signers)} of {self.n} required signers')

        # Check if name used before
        if name in [signer["name"] for signer in self.signers]:
            raise JunctionError(f'Name "{name}" already taken')

        # check if fingerprint used before
        if fingerprint in [signer["fingerprint"] for signer in self.signers]:
            raise JunctionError(f'Fingerprint "{fingerprint}" already used')

        self.signers.append({"name": name, "fingerprint": fingerprint, "xpub": xpub})
        logger.info(f"Registered signer \"{name}\"")

        # Export next chunk watch-only addresses to Bitcoin Core if we're done adding signers
        if self.ready():
            self.export_watchonly()

        self.save()

    def remove_signer(signer_name):
        raise NotImplementedError()

    def descriptor(self):
        '''Descriptor for shared multisig addresses'''
        # TODO: consider using HWI's Descriptor class
        origin_path = "/44h/1h/0h"
        path_suffix = "/0/*"
        xpubs = [f'[{signer["fingerprint"]}{origin_path}]{signer["xpub"]}{path_suffix}' for signer in self.signers]
        xpubs = ",".join(xpubs)
        descriptor = f"wsh(multi({self.m},{xpubs}))"
        logger.info(f"Exporting descriptor: {descriptor}")
        # validates and appends checksum
        r = self.wallet_rpc.getdescriptorinfo(descriptor)
        return r['descriptor']

    def address(self):
        # TODO: this check could work nicely as a decorator
        if not self.ready():
            raise JunctionError(f'{self.n} signers required, {len(self.signers)} registered')
        address = self.wallet_rpc.deriveaddresses(
            self.descriptor(), 
            [self.address_index, self.address_index + 1])[0]
        self.address_index += 1
        self.save()
        return address

    def create_watchonly(self):
        # Create watch-only Bitcoin Core wallet (FIXME super ugly)
        # Prefix the wallet name with "junction_" to make it clear this is a junction wallet
        watch_only_name = self.watchonly_name()
        bitcoin_wallets = bitcoin_rpc.listwallets()
        if watch_only_name not in bitcoin_wallets:
            try:
                bitcoin_rpc.loadwallet(watch_only_name)
                logger.info(f"Loaded watch-only Bitcoin Core wallet \"{watch_only_name}\"")
            except JSONRPCException as e:
                try:
                    bitcoin_rpc.createwallet(watch_only_name, True)
                    logger.info(f"Created watch-only Bitcoin Core wallet \"{watch_only_name}\"")
                except JSONRPCException as e:
                    raise JunctionError("Couldn't establish watch-only Bitcoin Core wallet")

    def watchonly_name(self):
        # maybe add a "junction_" prefix or something?
        return self.name

    def export_watchonly(self):
        logger.info("Starting watch-only export")
        self.wallet_rpc.importmulti([{
            "desc": self.descriptor(),
            "timestamp": "now",
            "range": [self.address_index, settings["wallet"]["address_chunk"]],
            "watchonly": True,
            "keypool": True,
            "internal": False,
        }])
        logger.info("Finished watch-only export")

    def create_psbt(self, recipient, amount):
        if self.psbt:
            raise JunctionError('PSBT already present')
        # FIXME bitcoin core can't generate change addrs
        change_address = self.address()
        raw_psbt = self.wallet_rpc.walletcreatefundedpsbt(
            # let Bitcoin Core choose inputs
            [],
            # Outputs
            [{recipient: amount}],
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
        return self.wallet_rpc.decodepsbt(self.psbt.serialize())

    def broadcast(self):
        psbt_hex = self.psbt.serialize()
        tx_hex = self.wallet_rpc.finalizepsbt(psbt_hex)["hex"]
        return self.wallet_rpc.sendrawtransaction(tx_hex)
