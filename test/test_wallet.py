import unittest
import tempfile
import os
import logging
from decimal import Decimal
from junction import MultisigWallet, JunctionError

from .utils import start_bitcoind

import disk
from utils import JSONRPCException

# uncomment for logging output in tests
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

derivation_path = "m/44h/1h/0h"

# FIXME: generate xpubs randomly ...
signers = [
    {
        'name': 'mytrezor',
        'type': 'trezor',
        'fingerprint': 'ecbc6bc1',
        'xpub': 'tpubDDsVS9pwqzLB92RZ6uTiixhDLPcoL1JESsYUCGootaTYu4JVh1aCu5t9oY3RRC1ic2dAbt7AqsE8uXLeq1p2DC5SP27ntmx4dUUPnvWhNhW',
        'derivation_path': derivation_path,
    },
    {
        'name': 'myledger',
        'type': 'ledger',
        'fingerprint': '6bb3d403',
        'xpub': 'tpubDCpR7Xjiho9KdidtHf3gJ1ZRbzu64HAiYTG9vR6JE5jJrPZbqJYBVXT33rFboKG8PBh4rJudjpBjFjD4ADwdwKUdMYZGJr2bBvLNBZLPMyF',
        'derivation_path': derivation_path,
    },
    {
        'name': 'mycoldcard',
        'type': 'coldcard',
        'fingerprint': '5b98d98d',
        'xpub': 'tpubDDSFSPwTa8AnvogHXTsJ29745CDLrSmn9Jsi5LN9ks1T6szBk7xmkNAjZ1gXfQHdfuD1rae939z93rXE7he3QkLxNmaLh1XuvyzZoTAAWYm',
        'derivation_path': derivation_path,
    },
]

def make_wallet_file(wallet_name):
    wallet_file = {
        'name': wallet_name,
        'm': 2,
        'n': 3,
        'signers': signers,
        'psbts': [],
        'receiving_address_index': 0,
        'receiving_export_index': 100,
        'change_address_index': 0,
        'change_export_index': 100,
    }
    disk.write_json_file(wallet_file, f'wallets/{wallet_name}.json')

def make_wallet(wallet_name):
    wallet = MultisigWallet.create(wallet_name, 2, 3)
    for signer in signers:
        wallet.add_signer(**signer)
    return wallet

class WalletTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = 10000  # FIXME: descriptor test maxed out this parameter
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
            'rpc': {
                'host': '127.0.0.1',
                'port': 18443,
                'user': self.rpc_username,
                'password': self.rpc_password,
            },
        }
        disk.ensure_datadir()
        disk.write_json_file(settings, 'settings.json')

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
        wallet.add_signer(**signers[0])
        self.assertFalse(wallet.ready())

        # add second signer
        wallet.add_signer(**signers[1])
        self.assertFalse(wallet.ready())

        # can't add same signer twice
        with self.assertRaises(JunctionError):
            wallet.add_signer(**signers[1])

        # add third signer
        wallet.add_signer(**signers[2])
        self.assertTrue(wallet.ready())
        # check that we can derive addresses
        self.assertIsNotNone(wallet.address(True))
        self.assertIsNotNone(wallet.address(False))
        
        # can't add more signers once wallet "ready"
        with self.assertRaises(JunctionError):
            wallet.add_signer(name='x', fingerprint='x', xpub='x', type='x', derivation_path='x')

    def test_create_wallet_already_exists(self):
        disk.write_json_file({}, 'wallets/test_create_wallet_already_exists.json')
        with self.assertRaises(JunctionError):
            wallet = MultisigWallet.create('test_create_wallet_already_exists', 2, 3)

    @unittest.skip('still deciding correct behavior')
    def test_watchonly_already_exists(self):
        self.rpc.createwallet('test_watchonly_already_exists')
        wallet = MultisigWallet.create('test_watchonly_already_exists', 2, 3)
        wallet.add_signer(**signers[0])
        wallet.add_signer(**signers[1])
        # not sure what right behavior is here
        # maybe we can verify that the old watch-only wallet
        # has same addresses? we don't want non-junction utxos showing up ...
        with self.assertRaises(JSONRPCException):
            wallet.add_signer(**signers[2])

    def test_open_wallet_file_doesnt_exist(self):
        with self.assertRaises(FileNotFoundError):
            MultisigWallet.open('test_open_wallet_doesnt_exist')

    def test_open_wallet_watchonly_doesnt_exist(self):
        make_wallet_file(self._testMethodName)
        # watch-only wallet doesn't exist
        self.assertNotIn(self._testMethodName, self.rpc.listwallets())
        # load wallet
        wallet = MultisigWallet.open(self._testMethodName)
        # watch-only wallet was created
        self.assertIn(self._testMethodName, self.rpc.listwallets())

    def test_save_wallet(self):
        '''Open and save is idempotent'''
        # TODO: try to make sure that wallet files can't be overwritten accidentally
        make_wallet_file(self._testMethodName)
        wallet_file_path = os.path.join(self.wallet_dir, f'{self._testMethodName}.json')
        with open(wallet_file_path, 'r') as f:
            initial_contents = f.read()
        wallet = MultisigWallet.open(self._testMethodName)
        wallet.save()
        with open(wallet_file_path, 'r') as f:
            final_contents = f.read()
        assert initial_contents == final_contents

    def test_descriptor(self):
        wallet = make_wallet(self._testMethodName)
        want = "wsh(multi(2,[ecbc6bc1/44'/1'/0']tpubDDsVS9pwqzLB92RZ6uTiixhDLPcoL1JESsYUCGootaTYu4JVh1aCu5t9oY3RRC1ic2dAbt7AqsE8uXLeq1p2DC5SP27ntmx4dUUPnvWhNhW/0/*,[6bb3d403/44'/1'/0']tpubDCpR7Xjiho9KdidtHf3gJ1ZRbzu64HAiYTG9vR6JE5jJrPZbqJYBVXT33rFboKG8PBh4rJudjpBjFjD4ADwdwKUdMYZGJr2bBvLNBZLPMyF/0/*,[5b98d98d/44'/1'/0']tpubDDSFSPwTa8AnvogHXTsJ29745CDLrSmn9Jsi5LN9ks1T6szBk7xmkNAjZ1gXfQHdfuD1rae939z93rXE7he3QkLxNmaLh1XuvyzZoTAAWYm/0/*))#qhjc39jj"
        self.assertEqual(want, wallet.descriptor(False))

    def test_export(self):
        self.rpc.generatetoaddress(1, self.rpc.getnewaddress())
        wallet = make_wallet(self._testMethodName)
        count = len(wallet.wallet_rpc.listtransactions())
        while wallet.receiving_address_index < 201 :  # cross address export boundary
            address = wallet.address(False)
            ai = wallet.wallet_rpc.getaddressinfo(address)
            # Check BIP67
            self.assertEqual(ai['pubkeys'], sorted(ai['pubkeys']))
            self.rpc.sendtoaddress(address, .1)
            count += 1
        self.rpc.generatetoaddress(1, self.rpc.getnewaddress())
        self.assertEqual(len(wallet.wallet_rpc.listtransactions('*', 1000)), count)

    def test_create_psbt(self):
        # fixture: get some coins for coin selection
        # check that receiver and change addresses are correct
        # check that bitcoin core funds the psbt
        wallet = make_wallet(self._testMethodName)
        # fund out wallet
        self.rpc.sendtoaddress(wallet.address(False), 1)
        self.rpc.generatetoaddress(1, self.rpc.getnewaddress())
        # create psbt
        receiving_address = self.rpc.getnewaddress()
        outputs = [{receiving_address: Decimal('0.0001')}]
        wallet.create_psbt(outputs)
        self.assertTrue(len(wallet.psbts) > 0)  # FIXME
        psbt = wallet.decode_psbt(wallet.psbts[0])

        # receiving address is in the outputs
        output_addrs = [vout['scriptPubKey']['addresses'][0] for vout in psbt['tx']['vout']]
        self.assertIn(receiving_address, output_addrs)
        output_addrs.remove(receiving_address)
        change_addrs = wallet.wallet_rpc.deriveaddresses(
            wallet.descriptor(True), 
            [0, wallet.export_index + 1])  # FIXME: +1 just to be safe

        # the remaining output address (change) belongs to wallet
        self.assertIn(output_addrs[0], change_addrs)

    def test_signing_complete(self):
        # test with finished and unfinished psbts
        pass
