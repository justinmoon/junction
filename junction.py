import json
import logging
import os.path

import toml

from bitcoinlib.keys import HDKey
from bitcoinlib.services.authproxy import AuthServiceProxy, JSONRPCException

from signer import InsecureSigner


logger = logging.getLogger(__name__)

settings = toml.load("settings.toml")

bitcoin_uri = "http://{username}:{password}@{host}:{port}"
bitcoin_rpc = AuthServiceProxy(bitcoin_uri.format(**settings["rpc"]))


class Multisig:

    wallet_uri = "http://{username}:{password}@{host}:{port}/wallet/junction"

    def __init__(self, name, m, n, signers, psbt, address_index):
        self.name = name        # name of the wallet
        self.m = m              # signers required for bitcoin tx
        self.n = n              # total signers
        self.signers = signers  # dictionary
        self.psbt = psbt        # hex string
        self.address_index = address_index
        self.wallet_rpc = AuthServiceProxy(self.wallet_uri.format(**settings["rpc"]))

    @classmethod
    def create(cls, name, m, n):
        # Never overwrite existing wallet files
        filename = f"junction_{name}.json"
        if os.path.exists(filename):
            raise RuntimeError(f"{filename} already exists")

        # Create watch-only Bitcoin Core wallet (FIXME)
        walletname = f"junction_{name}"
        walletnames = bitcoin_rpc.listwallets()
        if walletname not in walletnames:
            loaded = False
            try:
                bitcoin_rpc.loadwallet(walletname)
                logger.info(f"Loaded watch-only Bitcoin Core wallet \"{walletname}\"")
                loaded = True
            except JSONRPCException as e:
                pass
            if not loaded:
                try:
                    bitcoin_rpc.createwallet(walletname, True)
                    logger.info(f"Created watch-only Bitcoin Core wallet \"{walletname}\"")
                except JSONRPCException as e:
                    raise RuntimeError("Couldn't establish watch-only Bitcoin Core wallet")


        # Multisig instance
        multisig = cls(name, m, n, {}, None, 0)

        # Save a copy of wallet to disk
        multisig.save()

        # Return instance
        return multisig

    @classmethod
    def open(cls, filename):
        with open(filename) as f:
            multisig = cls.deserialize(json.load(f))
            logger.info(f"Opened wallet from {filename}")
            return multisig

    def save(self):
        filename = f"wallet-{self.name}.json"
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f)
            logger.info(f"Saved wallet to {filename}")

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["name"],
            m=d["m"],
            n=d["n"],
            signers=Signer.from_dict(d["signers"]),
            psbt=d["psbt"],
        )
        
    def to_dict(self):
        return {
            "name": self.name,
            "m": self.m,
            "n": self.n,
            "signers": {signer.name: signer.serialize() for signer in self.signers},
            "psbt": self.psbt,
        }

    def add_signer(self, signer):
        self.signers[signer.name] = signer
        logger.info(f"Registered signer \"{signer.name}\"")

    def remove_signer(signer_name):
        del self.signers[signer_name]

    def descriptor(self):
        '''Descriptor for shared multisig addresses'''
        xpubs = ",".join([signer.xpub() + "/*" for signer in self.signers.values()])
        descriptor = f"wsh(multi({self.n},{xpubs}))"
        # appends checksum to descriptor
        return self.wallet_rpc.getdescriptorinfo(descriptor)['descriptor']

    def consume_address(self):
        # generator to yield new addresses?
        address = self.wallet_rpc.deriveaddresses(
            self.descriptor(), 
            [self.address_index, self.address_index + 1])[0]
        self.address_index += 1
        # save?
        return address

    def combine_psbt(self, psbt):
        pass

    def sign_psbt(self, signer_name, psbt):
        # self.signers[signer_name_name].sign(psbt)
        pass

    def complete_psbt(self):
        # combine
        # finalize
        # broadcast
        pass


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    # create multisig
    multisig = Multisig.create("test", 2, 2)

    # add a signer
    sa = InsecureSigner("a")
    multisig.add_signer(sa)

    # add another signer
    sb = InsecureSigner("b")
    multisig.add_signer(sb)
    
    # derive next address
    print(multisig.consume_address())


def cleanup():
    import os
    # os.remove("junction_test.json")
    # bitcoin_rpc.unloadwallet("junction_test")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        pass
    cleanup()
