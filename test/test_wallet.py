import unittest
import os

from .utils import start_bitcoind

class WalletTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        bitcoind_path = os.path.join(test_dir, 'bitcoin/src/bitcoind')
        cls.rpc, cls.userpass = start_bitcoind(bitcoind_path)

    def test_generate(self):
        balance = self.rpc.getbalance()
        self.assertEqual(50, int(balance))


