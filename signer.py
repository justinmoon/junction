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
        # output of `hwi enumerate`
        self.device = None

    def connect(self):
        pass



class InsecureSigner(Signer):

    type = "insecure"

    def __init__(self, name, key):
        self.name = name
        self.key = key

    @classmethod
    def create(cls, name):
        '''Handle conversions from wifs and things in here'''
        key = HDKey(network="testnet")
        return cls(name, key)

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
