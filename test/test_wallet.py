import unittest
import tempfile
import os
from junction import MultisigWallet, JunctionError

from .utils import start_bitcoind

import disk
from utils import JSONRPCException

derivation_path = "m/44h/1h/0h"
signers = [
    ('ledger', '6bb3d403', 'tpubDCpR7Xjiho9KdidtHf3gJ1ZRbzu64HAiYTG9vR6JE5jJrPZbqJYBVXT33rFboKG8PBh4rJudjpBjFjD4ADwdwKUdMYZGJr2bBvLNBZLPMyF', derivation_path),

    ('coldcard', '5b98d98d', 'tpubDDSFSPwTa8AnvogHXTsJ29745CDLrSmn9Jsi5LN9ks1T6szBk7xmkNAjZ1gXfQHdfuD1rae939z93rXE7he3QkLxNmaLh1XuvyzZoTAAWYm', derivation_path),
    ('trezor', 'ecbc6bc1', 'tpubDDsVS9pwqzLB92RZ6uTiixhDLPcoL1JESsYUCGootaTYu4JVh1aCu5t9oY3RRC1ic2dAbt7AqsE8uXLeq1p2DC5SP27ntmx4dUUPnvWhNhW', derivation_path),
]

class WalletTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        bitcoind_path = os.path.join(test_dir, 'bitcoin/src/bitcoind')
        cls.rpc, cls.rpc_username, cls.rpc_password = start_bitcoind(bitcoind_path)

    def setUp(self):
        # a hack to use a new temporary datadir for every unittest ...
        # sketch b/c conceivably unittests could interfere with real junction wallet files
        # if this isn't executed in testing ...
        disk.DATADIR = tempfile.mktemp()
        self.wallet_dir = os.path.join(disk.DATADIR, 'wallets')  # FIXME
        settings = {
            'rpc_host': '127.0.0.1',
            'rpc_port': 18443,
            'rpc_username': self.rpc_username,
            'rpc_password': self.rpc_password,
            'address_chunk': 100,
        }
        disk.ensure_datadir()
        disk.write_json_file(settings, 'settings.json')

    def test_generate(self):
        balance = self.rpc.getbalance()
        self.assertEqual(50, int(balance))

    def test_create_wallet_wrong_parameters(self):
        # m > n
        with self.assertRaises(JunctionError):
            wallet = MultisigWallet.create('unittest__test_create_wallet', 3, 2)
        # n must be positive
        with self.assertRaises(JunctionError):
            wallet = MultisigWallet.create('unittest__test_create_wallet', 0, 1)
        # m capped at 5
        with self.assertRaises(JunctionError):
            wallet = MultisigWallet.create('unittest__test_create_wallet', 3, 6)

    def test_create_wallet_valid_2_of_3(self):
        wallet = MultisigWallet.create('unittest__test_create_wallet', 2, 3)
        # wallet file created
        self.assertIn(f'{wallet.name}.json', os.listdir(self.wallet_dir))
        # TODO: assert that it has correct attributes
        # watch-only wallet created
        self.assertIn(wallet.name, self.rpc.listwallets())

        # add first signer
        derivation_path = "m/44h/1h/0h"
        wallet.add_signer(*signers[0])
        self.assertFalse(wallet.ready())

        # add second signer
        wallet.add_signer(*signers[1])
        self.assertFalse(wallet.ready())

        # can't add same signer twice
        with self.assertRaises(JunctionError):
            wallet.add_signer(*signers[1])

        # add third signer
        wallet.add_signer(*signers[2])
        self.assertTrue(wallet.ready())
        # check that we can derive addresses
        self.assertIsNotNone(wallet.address())

        # can't add more signers once wallet "ready"
        with self.assertRaises(JunctionError):
            wallet.add_signer('x', 'x', 'x', 'x')

    def test_create_wallet_already_exists(self):
        disk.write_json_file({}, 'wallets/test_create_wallet_already_exists.json')
        with self.assertRaises(JunctionError):
            wallet = MultisigWallet.create('test_create_wallet_already_exists', 2, 3)

    def test_watchonly_already_exists(self):
        self.rpc.createwallet('test_watchonly_already_exists')
        wallet = MultisigWallet.create('test_watchonly_already_exists', 2, 3)
        wallet.add_signer(*signers[0])
        wallet.add_signer(*signers[1])
        # not sure what right behavior is here
        # maybe we can verify that the old watch-only wallet
        # has same addresses? we don't want non-junction utxos showing up ...
        with self.assertRaises(JSONRPCException):
            wallet.add_signer(*signers[2])

        # watch-only wallet
        # - is created
        # - importmulti is called
        # - right behavior when watch-only wallet with same name already exists

        # wallet file
        # - is created
        # - not deleted when it shouldn't be
        # 
        # can we create an pre-existing transaction and test that bitcoind finds it?
        pass

    def test_open_wallet(self):
        # watch-only wallet doesn't exist (what to do?)
        # wallet file doesn't exist (JunctionError?)
        # watch-only wallet exists, is loaded
        pass

    def test_save_wallet(self):
        # try to make sure that wallet files can't be overwritten accidentally
        # open and save is idempotent
        pass

    def test_descriptor(self):
        pass

    def test_address(self):
        # generate N new addresses, make sure that none violate BIP67
        pass

    def test_export(self):
        # generate wallet, export N addresses, send to each of the addresses, 
        # check that bitcoin core finds N transactions
        pass

    def test_create_psbt(self):
        # fixture: get some coins for coin selection
        # check that receiver and change addresses are correct
        # check that bitcoin core funds the psbt
        pass

    def test_signing_complete(self):
        # test with finished and unfinished psbts
        pass
