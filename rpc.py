from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


class RPC:

    def __init__(self, uri):
        self.rpc = AuthServiceProxy(uri)

    def __getattr__(self, name):
        tries_remaining = 5
        try:
            r = getattr(self.rpc, name)
        except:
            if tries_remaining > 0:
                tries_remaining -= 1
                print('retrying')
                r = getattr(self.rpc, name)
            else:
                raise
        return r  # FIXME



