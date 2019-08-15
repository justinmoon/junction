import json
from os import listdir
from decimal import Decimal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def write_json_file(data, filename):
    with open(filename, 'w') as f:
        return json.dump(data, f, indent=4)

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def test_rpc(rpc_settings):
    # FIXME: this rpc_settings variable is whack
    uri = "http://{username}:{password}@{host}:{port}"
    rpc = RPC(uri.format(**rpc_settings))
    try:
        rpc.getblockchaininfo()
        return True
    except:
        return False

def wallets_exist():
    return bool(listdir('wallets'))

def get_first_wallet_name():
    file_name = listdir('wallets')[0]
    wallet_name = file_name.split('.')[0]
    return wallet_name
    
###  Currency conversions

COIN_PER_SAT = Decimal(10) ** -8
SAT_PER_COIN = 100_000_000

def btc_to_sat(btc):
    return int(btc*SAT_PER_COIN)

def sat_to_btc(sat):
    return Decimal(sat/100_000_000).quantize(COIN_PER_SAT)



### RPC


class RPC:

    def __init__(self, uri):
        self.uri = uri

    def __getattr__(self, name):
        rpc = AuthServiceProxy(self.uri, timeout=60*10)  # 10 minute timeout
        tries_remaining = 5
        try:
            r = getattr(rpc, name)
        except:
            if tries_remaining > 0:
                tries_remaining -= 1
                r = getattr(self.rpc, name)
            else:
                raise
        return r  # FIXME


### ColdCard

# FIXME: do this with hwilib.devices.coldcard
# `real_file_upload` is the only thing that's missing
from utils import get_first_wallet_name
from ckcc.cli import ColdcardDevice, real_file_upload, MAX_BLK_LEN, CCProtocolPacker
from io import BytesIO

multisig_header = \
"""Name: {name}
Policy: {m} of {n}
Derivation: {path}
Format: {format}

"""
multisig_key = \
"\n{fingerprint}: {xpub}"

def coldcard_multisig_file(wallet):
    contents = multisig_header.format(name=wallet.name, m=wallet.m, n=wallet.n, 
                                      path="m/44'/1'/0'", format='P2SH')
    for signer in wallet.signers:
        contents += multisig_key.format(fingerprint=signer['fingerprint'],
                                        xpub=signer['xpub'])

    return BytesIO(contents.encode())

def coldcard_enroll(wallet):
    multisig_file = coldcard_multisig_file(wallet)

    force_serial = None
    dev = ColdcardDevice(sn=force_serial)

    file_len, sha = real_file_upload(multisig_file, MAX_BLK_LEN, dev=dev)

    dev.send_recv(CCProtocolPacker.multisig_enroll(file_len, sha))

