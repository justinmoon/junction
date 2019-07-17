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

    def __init__(self, name, path, fingerprint, xpub):
        # output of `hwi enumerate`
        self.name = name
        # next two from HWI's "enumerate" command
        self.path = path
        self.fingerprint = fingerprint
        # from HWI's "getmasterxpub" command
        self.xpub = xpub

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return {
            'name': self.name,
            'path': self.path,
            'fingerprint': self.fingerprint,
            'xpub': self.xpub,
        }


class InsecureSigner(Signer):

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
