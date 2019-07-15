from bitcoinrpc.authproxy import AuthServiceProxy



class RPC:

    rpc_template = "http://%s:%s@%s:%s/wallet/%s"

    def __init__(self, wallet=""):
        uri = self.rpc_template % ('bitcoin', 'python', 'localhost', 18332, wallet)
        self.rpc = AuthServiceProxy(uri, timeout=120)

    def __getattr__(self, name):
        """Hack to establish a new AuthServiceProxy every time this is called"""
        return getattr(self.rpc, name)
