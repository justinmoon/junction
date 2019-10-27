import unittest
import tempfile
import os
import logging
from decimal import Decimal
from junction import Wallet, JunctionError, Node

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

def make_node(testcase):
    wallet_name = testcase._testMethodName
    return Node(
        host='127.0.0.1',
        port=18443,
        user=testcase.rpc_user,
        password=testcase.rpc_password,
        wallet_name=wallet_name,
        network='testnet',
    )

def make_wallet_file(testcase):
    wallet_name = testcase._testMethodName
    wallet_file = {
        'name': wallet_name,
        'm': 2,
        'n': 3,
        'signers': signers,
        'psbts': [],
        'receiving_address_index': 0,
        'change_address_index': 0,
        'network': 'testnet',
        'script_type': 'native',
        'node': {
            'host': '127.0.0.1',
            'port': 18443,
            'user': testcase.rpc_user,
            'password': testcase.rpc_password,
            'wallet_name': wallet_name,
            'network': 'testnet',
        },
    }
    disk.write_json_file(wallet_file, f'wallets/{wallet_name}.json')

def make_wallet(testcase):
    wallet_name = testcase._testMethodName
    node = make_node(testcase)
    wallet = Wallet.create(
        name=wallet_name,
        m=2,
        n=3,
        node=node,
        network=node.network,
        script_type='native',
    )
    for signer in signers:
        wallet.add_signer(**signer)
    return wallet

class WalletTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = 10000  # FIXME: descriptor test maxed out this parameter
        test_dir = os.path.dirname(os.path.realpath(__file__))
        bitcoind_path = os.path.join(test_dir, 'bitcoin/src/bitcoind')
        cls.rpc, cls.rpc_user, cls.rpc_password = start_bitcoind(bitcoind_path)

    def setUp(self):
        # a hack to use a new temporary datadir for every unittest ...
        # sketch b/c conceivably unittests could interfere with real junction wallet files
        # if this isn't executed in testing ...
        disk.DATADIR = tempfile.mktemp()
        self.wallet_dir = os.path.join(disk.DATADIR, 'wallets')  # FIXME
        # self.node = {
        #     'host': '127.0.0.1',
        #     'port': 18443,
        #     'user': self.rpc_user,
        #     'password': self.rpc_password,
        #     'wallet_name': 'foobar',
        # }
        disk.ensure_datadir()

    def test_create_wallet_wrong_parameters(self):
        wallet_name = self._testMethodName
        node = make_node(self)
        # m > n
        with self.assertRaises(JunctionError):
            Wallet.create(
                name=wallet_name,
                m=3,
                n=2,
                node=node,
                network=node.network,
                script_type='native',
            )
        # n must be positive
        with self.assertRaises(JunctionError):
            Wallet.create(
                name=wallet_name,
                m=0,
                n=1,
                node=node,
                network=node.network,
                script_type='native',
            )
        # m capped at 5
        with self.assertRaises(JunctionError):
            Wallet.create(
                name=wallet_name,
                m=3,
                n=21,
                node=node,
                network=node.network,
                script_type='native',
            )

    def test_add_signers(self):
        node = make_node(self)
        wallet = Wallet.create(name=self._testMethodName, m=2, n=3, node=node,
            script_type='native', network='regtest')

        # Wallet file created
        self.assertIn(f'{wallet.name}.json', os.listdir(self.wallet_dir))
        # TODO: assert that it has correct attributes

        # Bitcoin Core watch-only wallet created
        self.assertIn(wallet.name, self.rpc.listwallets())

        # Add first signer
        wallet.add_signer(**signers[0])
        self.assertFalse(wallet.ready())

        # Add second signer
        wallet.add_signer(**signers[1])
        self.assertFalse(wallet.ready())

        # Can't add same signer twice
        with self.assertRaises(JunctionError):
            wallet.add_signer(**signers[1])

        # Add third signer
        wallet.add_signer(**signers[2])
        self.assertTrue(wallet.ready())
        
        # Can't add signers once wallet "ready"
        with self.assertRaises(JunctionError):
            wallet.add_signer(name='x', fingerprint='x', xpub='x', type='x', derivation_path='x')

    def test_create_wallet_already_exists(self):
        wallet_name = self._testMethodName
        disk.write_json_file({}, f'wallets/{wallet_name}.json')
        with self.assertRaises(JunctionError):
            wallet = make_wallet(self)

    @unittest.skip('still deciding correct behavior')
    def test_watchonly_already_exists(self):
        wallet_name = self._testMethodName
        self.rpc.createwallet(wallet_name)
        wallet = make_wallet(self)
        wallet.add_signer(**signers[0])
        wallet.add_signer(**signers[1])
        # not sure what right behavior is here
        # maybe we can verify that the old watch-only wallet
        # has same addresses? we don't want non-junction utxos showing up ...
        with self.assertRaises(JSONRPCException):
            wallet.add_signer(**signers[2])

    def test_open_wallet_file_doesnt_exist(self):
        with self.assertRaises(FileNotFoundError):
            Wallet.open('test_open_wallet_doesnt_exist')

    def test_open_wallet_watchonly_doesnt_exist(self):
        make_wallet_file(self)
        # watch-only wallet doesn't exist
        self.assertNotIn(self._testMethodName, self.rpc.listwallets())
        # load wallet
        wallet = Wallet.open(self._testMethodName)
        # watch-only wallet was created
        self.assertIn(self._testMethodName, self.rpc.listwallets())

    def test_save_wallet(self):
        '''Open and save is idempotent'''
        # TODO: try to make sure that wallet files can't be overwritten accidentally
        wallet = make_wallet(self)
        wallet_name = self._testMethodName
        wallet_file_path = os.path.join(self.wallet_dir, f'{wallet_name}.json')
        with open(wallet_file_path, 'r') as f:
            initial_contents = f.read()
        wallet = Wallet.open(wallet_name)
        wallet.save()
        with open(wallet_file_path, 'r') as f:
            final_contents = f.read()
        self.assertEqual(initial_contents, final_contents)

    def test_address_derivation(self):
        wallet = make_wallet(self)

        # Address indices initialize correctly
        self.assertEqual(wallet.receiving_address_index, 0)
        self.assertEqual(wallet.change_address_index, 0)
        
        # Can derive addresses
        receiving_address = wallet.derive_receiving_address()
        self.assertIsNotNone(receiving_address)
        change_address = wallet.derive_change_address()
        self.assertIsNotNone(change_address)

        # Address indices update correctly
        self.assertEqual(wallet.receiving_address_index, 1)
        self.assertEqual(wallet.change_address_index, 1)

        # Look up addresses in Bitcoin Core
        receiving_address_info = wallet.node.wallet_rpc.getaddressinfo(receiving_address)
        change_address_info = wallet.node.wallet_rpc.getaddressinfo(change_address)

        # Bitcoin Core watch-only wallet is watching these addresses
        self.assertTrue(receiving_address_info.get('iswatchonly'))
        self.assertTrue(change_address_info.get('iswatchonly'))

        # Bitcoin Core correctly understands which is change / receiving
        self.assertFalse(receiving_address_info['ischange'])
        self.assertTrue(change_address_info['ischange'])

        # Two transactions show up in watch-only wallet if we send one output to each address
        self.assertEqual(len(wallet.node.wallet_rpc.listtransactions('*', 1000)), 0)
        self.rpc.sendtoaddress(receiving_address, 1)
        self.rpc.sendtoaddress(change_address, 1)
        self.assertEqual(len(wallet.node.wallet_rpc.listtransactions('*', 1000)), 2)
    
    def test_descriptor(self):
        raise NotImplementedError('cover every script type and wallet type')
        wallet = make_wallet(self)
        want = "wsh(multi(2,[ecbc6bc1/44'/1'/0']tpubDDsVS9pwqzLB92RZ6uTiixhDLPcoL1JESsYUCGootaTYu4JVh1aCu5t9oY3RRC1ic2dAbt7AqsE8uXLeq1p2DC5SP27ntmx4dUUPnvWhNhW/0/*,[6bb3d403/44'/1'/0']tpubDCpR7Xjiho9KdidtHf3gJ1ZRbzu64HAiYTG9vR6JE5jJrPZbqJYBVXT33rFboKG8PBh4rJudjpBjFjD4ADwdwKUdMYZGJr2bBvLNBZLPMyF/0/*,[5b98d98d/44'/1'/0']tpubDDSFSPwTa8AnvogHXTsJ29745CDLrSmn9Jsi5LN9ks1T6szBk7xmkNAjZ1gXfQHdfuD1rae939z93rXE7he3QkLxNmaLh1XuvyzZoTAAWYm/0/*))#qhjc39jj"
        self.assertEqual(want, wallet.descriptor(False))

    def test_sync(self):
        # Make wallet and bump address indices to 100
        wallet = make_wallet(self)
        wallet.change_address_index = wallet.receiving_address_index = 100

        # Get first 100 change and receiving addresses
        change_addresses = [wallet.node.wallet_rpc.deriveaddresses(wallet.descriptor(True, i))[0] for i in range(100)]
        receiving_addresses = [wallet.node.wallet_rpc.deriveaddresses(wallet.descriptor(False, i))[0] for i in range(100)]

        # Assert they aren't being watched
        for address in change_addresses + receiving_addresses:
            watching = wallet.node.wallet_rpc.getaddressinfo(address).get('iswatchonly')
            self.assertFalse(watching)
        
        # Sync addresses with Bitcoin Core 
        wallet.sync()

        # Assert they aren't being watched
        for index, address in enumerate(change_addresses + receiving_addresses):
            watching = wallet.node.wallet_rpc.getaddressinfo(address).get('iswatchonly')
            self.assertTrue(watching) 

    def test_create_psbt(self):
        # fixture: get some coins for coin selection
        # check that receiver and change addresses are correct
        # check that bitcoin core funds the psbt
        wallet = make_wallet(self)
        
        # fund our wallet
        self.rpc.generatetoaddress(1000, self.rpc.getnewaddress())
        self.rpc.sendtoaddress(wallet.derive_receiving_address(), 1)
        self.rpc.generatetoaddress(1, self.rpc.getnewaddress())

        # create psbt
        outgoing_address = self.rpc.getnewaddress()
        outputs = [{outgoing_address: Decimal('0.0001')}]
        wallet.create_psbt(outputs)
        self.assertTrue(len(wallet.psbts) > 0)  # FIXME
        psbt = wallet.decode_psbt(wallet.psbts[0])

        # 2 outputs
        output_addresses = [vout['scriptPubKey']['addresses'][0] for vout in psbt['tx']['vout']]
        self.assertEqual(len(output_addresses), 2)

        # receiving address is in the outputs
        self.assertIn(outgoing_address, output_addresses)        
        
        # the remaining output address (change) belongs to wallet
        change_address = wallet.derive_address(True, wallet.change_address_index-1)
        self.assertIn(change_address, output_addresses)

    def test_signing_complete(self):
        # test with finished and unfinished psbts
        pass

    def test_sort_multisig_pubkeys(self):
        '''Check that junction matches behavior of unreleased "sortedmulti" descriptor'''
        # Use "sortedmulti" to derive first num_addresses receiving addresses
        num_addresses = 100
        wallet = make_wallet(self)
        change = False
        xpubs = [f'[{signer.fingerprint}{signer.derivation_path[1:]}]{signer.xpub}/{int(change)}/*' 
                for signer in wallet.signers]
        xpubs = ",".join(xpubs)
        descriptor = f"wsh(sortedmulti({wallet.m},{xpubs}))"
        descriptor = wallet.node.wallet_rpc.getdescriptorinfo(descriptor)['descriptor']
        sortedmulti_addresses = address = wallet.node.default_rpc.deriveaddresses(descriptor, [0, num_addresses-1])
        self.assertEqual(num_addresses, len(sortedmulti_addresses))

        # Derive first N receiving addresses with junction
        junction_addresses = []
        for i in range(num_addresses):
            address = wallet.derive_receiving_address()
            junction_addresses.append(address)
        self.assertEqual(num_addresses, len(junction_addresses))

        # Check that they are equal
        self.assertEqual(sortedmulti_addresses, junction_addresses)