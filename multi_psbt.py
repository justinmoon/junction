from bitcoinlib.keys import HDKey

from rpc import RPC


rpc = RPC()

def generate_keys():
    with open("secret1.txt", "w") as f:
        hd1 = HDKey(network="testnet")
        f.write(hd1.wif_private())
    with open("secret2.txt", "w") as f:
        hd2 = HDKey(network="testnet")
        f.write(hd2.wif_private())


def load_keys():
    # get private keys
    with open("secret1.txt") as f:
        hd1 = HDKey(f.read(), network="testnet")
    with open("secret2.txt") as f:
        hd2 = HDKey(f.read(), network="testnet")
    return hd1, hd2


def derive_addresses(key1, key2):
    descriptor = descriptor_2_of_2(key1, key2)
    return rpc.deriveaddresses(descriptor, [0, 5])


def descriptor_2_of_2(key1, key2):
    xpub1 = key1.wif_public()
    xpub2 = key2.wif_public()
    raw_descriptor = f"wsh(multi(2,{xpub1}/*,{xpub2}/*))"
    descriptor = rpc.getdescriptorinfo(raw_descriptor)['descriptor']
    return descriptor


def import_addresses(key1, key2):
    rpc1 = RPC("multi-1")
    rpc2 = RPC("multi-2")
    descriptor = descriptor_2_of_2(key1, key2)
    import1 = rpc1.importmulti([{
        "desc" : descriptor, 
        "range" : [0, 1000], 
        "watchonly" : True, 
        "timestamp" : "now",
    }])
    print("import1 result:", import1)
    import2 = rpc2.importmulti([{
        "desc" : descriptor, 
        "range" : [0, 1000], 
        "watchonly" : True, 
        "timestamp" : "now",
    }])
    print("import2 result:", import2)


def main():
    key1, key2 = load_keys()
    import_addresses(key1, key2)

if __name__ == '__main__':
    main()

