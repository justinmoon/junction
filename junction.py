import json
import logging
import os.path
import hwilib
import toml

from bitcoinlib.services.authproxy import AuthServiceProxy, JSONRPCException
from pprint import pprint


logger = logging.getLogger(__name__)
settings = toml.load("settings.toml")

bitcoin_uri = "http://{username}:{password}@{host}:{port}"
bitcoin_rpc = AuthServiceProxy(bitcoin_uri.format(**settings["rpc"]))


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
        self.wallet_rpc = AuthServiceProxy(wallet_uri)

    def ready(self):
        return len(self.signers) == self.n

    def filename(self):
        return f"{self.name}.wallet"

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
            raise JunctionError(f"{filename} already exists")

        # create a watch-only Bitcoin Core wallet
        multisig.create_watchonly()

        # Save a copy of wallet to disk
        multisig.save()

        # Return instance
        return multisig

    @classmethod
    def open(cls, filename):
        with open(filename) as f:
            multisig = cls.from_dict(json.load(f))
            logger.info(f"Opened wallet from {filename}")
            return multisig

    def save(self):
        filename = self.filename()
        # if this line broke inside json.dump, the json file would be emptyed :eek:
        data = self.to_dict()  
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
            logger.info(f"Saved wallet to {filename}")
        # save a backup just in case
        with open(filename + '.bak', "w") as f:
            json.dump(data, f, indent=4)
            logger.info(f"Saved wallet to {filename}.bak")

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
            "psbt": self.psbt.serialize() if self.psbt else self.psbt,
            "address_index": self.address_index,
        }

    def add_signer(self, name, fingerprint, master_xpub, base_xpub):
        if self.ready():
            raise JunctionError(f'Already have {len(self.signers)} of {self.n} required signers')
        signer_names = [signer["name"] for signer in self.signers]
        if name in signer_names:
            raise JunctionError(f'Name "{signer.name}" already taken')
        self.signers.append({"name": name, "fingerprint": fingerprint, "xpub": master_xpub, "base_xpub": base_xpub})
        logger.info(f"Registered signer \"{name}\"")

        # Import next chunk of addresses into Bitcoin Core watch-only wallet if we're done adding signers
        if self.ready():
            self.export_watchonly()

        self.save()

    def remove_signer(signer_name):
        raise NotImplementedError()

    def descriptor(self):
        '''Descriptor for shared multisig addresses'''
        # TODO: consider using HWI's Descriptor class
        from utils import get_desc_part
        xpubs = [signer['xpub'] for signer in self.signers]
        parts = [get_desc_part(xpub, 0, False, False, False, True) for xpub in xpubs]
        # parts = ['['+signer["fingerprint"]+"/44h/1h/0h]"+signer['base_xpub']+'/0/*' for xpub in xpubs]
        print('parts', parts)
        inner = ",".join([part for part in parts])
        print('inner', inner)
        descriptor = f"wsh(multi({self.m},{inner}))"
        print(descriptor)
        # appends checksum to descriptor
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

        # cli.py can have user confirm and run with a force=True option or something
        # FIXME bitcoin core can't generate change addrs
        change_address = self.address()
        raw_psbt = self.wallet_rpc.walletcreatefundedpsbt(
            [],
            [{recipient: amount}],
            0, 
            {
                "includeWatching": True,
                "changeAddress": change_address,
            },
            True,
        )['psbt']
        self.psbt = hwilib.serializations.PSBT()
        self.psbt.deserialize(raw_psbt)
        self.save()

    def remove_psbt(self):
        self.psbt = None

    def decode_psbt(self):
        return self.wallet_rpc.decodepsbt(self.psbt.serialize())

    def broadcast(self):
        psbt_hex = self.psbt.serialize()
        print(self.wallet_rpc.finalizepsbt(psbt_hex))
        tx_hex = self.wallet_rpc.finalizepsbt(psbt_hex)["hex"]
        txid = self.wallet_rpc.sendrawtransaction(tx_hex)
        return txid
