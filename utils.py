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
