import json
from os import listdir
from rpc import RPC

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
    
