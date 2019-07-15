import json
import os.path

from bitcoinlib.keys import HDKey

from rpc import RPC


rpc = RPC()


class Multi2of2:

    filename = "state.json"

    def __init__(self, key1, key2, next_index):
        self.key1 = key1
        self.key2 = key2
        self.next_index = next_index
        self.rpc1 = RPC("multi-1")
        self.rpc2 = RPC("multi-2")
        self.chunk = 10

    @classmethod
    def init(cls):
        if os.path.exists(cls.filename):  # FIXME
            raise RuntimeError("state.json already exists")
        key1 = HDKey(network="testnet")
        key2 = HDKey(network="testnet")
        next_index = 0
        multi = cls(key1, key2, next_index)
        multi.commit()
        multi.export_bitcoind()
        return multi

    @classmethod
    def load(cls):
        with open(cls.filename) as f:
            state = json.load(f)
            return cls(
                HDKey(state["xprv1"]),
                HDKey(state["xprv2"]),
                state["next_index"],
            )

    def commit(self):
        state = {
            "xprv1": self.key1.wif_private(),
            "xprv2": self.key2.wif_private(),
            "next_index": self.next_index,
        }
        with open(self.filename, "w") as f:
            json.dump(state, f)

    def address(self):
        return rpc.deriveaddresses(
            self.descriptor(), 
            [self.next_index, self.next_index + 1])[0]

    def descriptor(self):
        xpub1 = self.key1.wif_public()
        xpub2 = self.key2.wif_public()
        raw_descriptor = f"wsh(multi(2,{xpub1}/*,{xpub2}/*))"
        # appends checksum to descriptor
        return rpc.getdescriptorinfo(raw_descriptor)['descriptor']

    def export_bitcoind(self):
        descriptor = self.descriptor()
        for rpc in (self.rpc1, self.rpc2):
            address_range = [self.next_index, self.next_index + self.chunk]
            result = rpc.importmulti([{
                "desc" : descriptor, 
                "range" : address_range, 
                "watchonly" : True, 
                "timestamp" : "now",
            }])
            if not result[0]["success"]:
                raise RuntimeError(f"Bitcoind export failed: {result}")
            print("Bitcoind export successful")


def main():
    if not os.path.exists(Multi2of2.filename):
        print("Initializing 2-of-2 multisig. This might take a while")
        multi = Multi2of2.init()
    else:
        print("Loading 2-of-2 multisig from disk")
        multi = Multi2of2.load()

    print(multi.address())

if __name__ == '__main__':
    main()

