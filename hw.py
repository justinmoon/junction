import sys

from hwilib.devices import ledger, digitalbitbox
from hwilib.commands import getkeypool
from bitcoinlib.keys import HDKey
from bitcoinrpc.authproxy import AuthServiceProxy
from hwilib.serializations import PSBT


bitboxes = digitalbitbox.enumerate()
ledgers = ledger.enumerate()


if len(ledgers):
    print("connecting to ledger")
    device_path = ledgers[0]['path']
    wallet_name = "ledger2"
    client = ledger.LedgerClient(device_path)
elif len(bitboxes):
    print("connecting to bitbox")
    password = sys.argv[1]
    bitboxes = digitalbitbox.enumerate(password=password)  # retry with password
    device_path = bitboxes[0]['path']
    wallet_name = "bitbox-1"
    print(device_path, password)
    client = digitalbitbox.DigitalbitboxClient(device_path, password)
else:
    print("no wallet plugged in")
    sys.exit()


def setup(wallet_name, device_path):
    keypool = getkeypool(client, None, 0, 1000, keypool=True)
    print("getkeypool:", keypool)

    createwallet = rpc.createwallet(wallet_name, True)
    print("createwallet:", createwallet)

    importmulti = rpc.importmulti(keypool, {"rescan": False})
    print("importmulti:", importmulti)


client.is_testnet = True


class RPC:

    def __init__(self, uri):
        self.rpc = AuthServiceProxy(uri, timeout=120)

    def __getattr__(self, name):
        """Hack to establish a new AuthServiceProxy every time this is called"""
        return getattr(self.rpc, name)


rpc_template = "http://%s:%s@%s:%s/wallet/%s"
# FIXME: I had to select "file > open wallet > ledger2" for this to work
# rpc = RPC(rpc_template % ('bitcoin', 'python', 'localhost', 18332, 'bitbox-1'))
rpc = RPC(rpc_template % ('bitcoin', 'python', 'localhost', 18332, wallet_name))




def sign_message():
    hd_path = "m/0'/0'/1'"
    return client.sign_message("hi friend", hd_path)


def get_address():
    _path = "m/1/2"  # FIXME
    raw_xpub = client.get_master_xpub()['xpub']
    xpub = HDKey(raw_xpub)
    child = xpub.subkey_for_path(_path, network='testnet')
    return child.address()


def send():
    # single-sig tx. ledger and coldcard separately.
    recipient = "tb1q7v4ynhl2z3rrqshnp96w3m4n2xnd7qr954az4z"  # bitboy
    recipient = "2N3YhAaK2fK7z2ghGgdbfhDnpUUDm5eA5bH"  # bitbox-1
    amount = "0.001"
    raw_psbt = rpc.walletcreatefundedpsbt(
        [],
        [{recipient: amount}],
        0, 
        {"includeWatching": True},
        True,
    )['psbt']
    print(rpc.decodepsbt(raw_psbt))
    user_input = input("Does this look correct? (y/n)")
    if user_input != 'y':
        return
    psbt = PSBT()
    psbt.deserialize(raw_psbt)
    print(psbt)
    signed_raw_psbt = client.sign_tx(psbt)["psbt"]
    print(signed_raw_psbt)
    print(rpc.finalizepsbt(signed_raw_psbt))
    tx_hex = rpc.finalizepsbt(signed_raw_psbt)["hex"]
    signed = rpc.sendrawtransaction(tx_hex)
    print("signed:", signed)


def prepare_psbt():
    # ask bitcoin core
    pass


def sign_psbt():
    # coldcard & ledger
    pass


if __name__ == '__main__':
    # setup("bitbox-1", device_path)
    send()
