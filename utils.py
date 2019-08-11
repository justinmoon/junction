import json

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
    rpc = AuthServiceProxy(uri.format(**rpc_settings))
    try:
        rpc.getblockchaininfo()
        return True
    except:
        return False


