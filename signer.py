from bitcoinlib.keys import HDKey



class Signer:

    def __init__(self, name):
        self.name = name

    @classmethod
    def from_dict(cls, d):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def sign(self, psbt):
        raise NotImplementedError

    def xpub(self):
        raise NotImplementedError


class HardwareSigner(Signer):

    def __init__(self):
        # fingerprint
        pass


class InsecureSigner(Signer):

    def __init__(self, name, key=None):
        self.name = name
        if not key:
            key = HDKey(network="testnet")
        self.key = key

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["name"],
            HDKey(d["xprv"], network="testnet"),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "xprv": self.key.wif_private(),
        }

    def xpub(self):
        return self.key.wif_public()
