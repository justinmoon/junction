import unittest

from utils import start_bitcoind

class WalletTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rpc, cls.userpass = start_bitcoind('./bitcoin/src/bitcoind')

    def test_generate(self):
        balance = self.rpc.getbalance()
        self.assertEqual(50, int(balance))


