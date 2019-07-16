import json
import logging
import os.path

import hwilib
import toml
from bitcoinlib.keys import HDKey
from bitcoinlib.services.authproxy import AuthServiceProxy, JSONRPCException

from signer import InsecureSigner

logger = logging.getLogger(__name__)

settings = toml.load("settings.toml")

bitcoin_uri = "http://{username}:{password}@{host}:{port}"
bitcoin_rpc = AuthServiceProxy(bitcoin_uri.format(**settings["rpc"]))


class MultiSig:

    wallet_uri = "http://{username}:{password}@{host}:{port}/wallet/{name}"

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
        wallet_uri = self.wallet_uri.format(**settings["rpc"], name=name)
        self.wallet_rpc = AuthServiceProxy(wallet_uri)

    def ready(self):
        return len(self.signers) == self.n

    def filename(self):
        return f"{self.name}.json"

    @classmethod
    def create(cls, name, m, n):
        # sanity check
        if m >= n:
            raise ValueError(f"\"m\" ({m}) must be no larger than \"n\" ({n})")

        # MultiSig instance
        multisig = cls(name, m, n, [], None, 0)

        # Never overwrite existing wallet files
        filename = multisig.filename()
        if os.path.exists(filename):
            raise RuntimeError(f"{filename} already exists")

        # Create watch-only Bitcoin Core wallet (FIXME super ugly)
        bitcoin_wallets = bitcoin_rpc.listwallets()
        if name not in bitcoin_wallets:
            try:
                bitcoin_rpc.loadwallet(name)
                logger.info(f"Loaded watch-only Bitcoin Core wallet \"{name}\"")
            except JSONRPCException as e:
                try:
                    bitcoin_rpc.createwallet(name, True)
                    logger.info(f"Created watch-only Bitcoin Core wallet \"{name}\"")
                except JSONRPCException as e:
                    raise RuntimeError("Couldn't establish watch-only Bitcoin Core wallet")

        # Import next chunk of addresses into ^^ Bitcoin Core watch-only wallet
        self.watch_only_export()

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
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
            logger.info(f"Saved wallet to {filename}")

    @classmethod
    def from_dict(cls, d):
        d["signers"] = [InsecureSigner.from_dict(s) for s in d["signers"]]
        return cls(**d)
        
    def to_dict(self):
        return {
            "name": self.name,
            "m": self.m,
            "n": self.n,
            "signers": [signer.to_dict() for signer in self.signers],
            "psbt": self.psbt,
            "address_index": self.address_index,
        }

    def add_signer(self, signer):
        if self.ready():
            raise ValueError(f'Already have {len(self.signers)} of {self.n} required signers')
        signer_names = [signer.name for signer in self.signers]
        if signer.name in signer_names:
            raise ValueError(f'Name "{signer.name}" already taken')
        self.signers.append(signer)
        logger.info(f"Registered signer \"{signer.name}\"")
        self.save()

    def remove_signer(signer_name):
        raise NotImplementedError()

    def descriptor(self):
        '''Descriptor for shared multisig addresses'''
        # TODO: this could work nicely as a decorator
        if not self.ready():
            raise ValueError(f'n signers required, {len(self.signers)} registered')
        xpubs = ",".join([signer.xpub() + "/*" for signer in self.signers])
        descriptor = f"wsh(multi({self.n},{xpubs}))"
        # appends checksum to descriptor
        return self.wallet_rpc.getdescriptorinfo(descriptor)['descriptor']

    def address(self):
        # generator to yield new addresses?
        address = self.wallet_rpc.deriveaddresses(
            self.descriptor(), 
            [self.address_index, self.address_index + 1])[0]
        self.address_index += 1
        self.save()
        return address

    def watch_only_export(self):
        logger.info("Starting watch-only export")
        self.wallet_rpc.importmulti([{
            "desc": self.descriptor(),
            "timestamp": "now",
            "range": [0, settings["wallet"]["address_chunk"]],
            "label": self.name,
            "watchonly": True,
            "keypool": True,
        }])
        logger.info("Finished watch-only export")

    def combine_psbt(self, psbt):
        raise NotImplementedError()

    def sign_psbt(self, signer_name, psbt):
        raise NotImplementedError()

    def complete_psbt(self):
        # combine
        # finalize
        # broadcast
        raise NotImplementedError()

    def candidates(self):
        # FIXME: this probably belongs in cli.py
        return hwilib.commands.enumerate()
