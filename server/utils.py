import json
import sys
import logging
from os import listdir
import os.path
from contextlib import contextmanager
from decimal import Decimal
from flask import flash, current_app as app
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from hwilib import commands
from hwilib.devices import coldcard, digitalbitbox, ledger, trezor
from btclib import bip32, base58
import http

logger = logging.getLogger(__name__)

### Exceptions

class JunctionError(Exception):
    pass

class JunctionWarning(Exception):
    pass

def handle_exception(exception):
    ''' prints the exception and most important the stacktrace '''
    logger.error("Unexpected error")
    logger.error("----START-TRACEBACK-----------------------------------------------------------------")
    logger.exception(exception)
    logger.error("----END---TRACEBACK-----------------------------------------------------------------")

### HWI

def get_device_for_client(client):
    devices = commands.enumerate()
    for device in devices:
        if client.path == device.path:
            return client

def get_device(device_id):
    matching_device = None
    for device in commands.enumerate():
        if device.get('path') == device_id:
            matching_device = device
        elif device.get('fingerprint') == device_id:
            matching_device = device
    if not matching_device:
        raise JunctionError('Device not found')
    return matching_device

def get_client(device, network):
    if device['type'] == 'ledger':
        client = ledger.LedgerClient(device['path'])
    elif device['type'] == 'coldcard':
        client = coldcard.ColdcardClient(device['path'])
    elif device['type'] == 'trezor':
        client = trezor.TrezorClient(device['path'])
    else:
        raise JunctionError(f'Devices of type "{device["type"]}" not yet supported')
    # FIXME: junction needs mainnet / testnet flag somewhere ...
    client.is_testnet = network != "mainnet"
    return client

@contextmanager
def get_client_and_device(device_id, network):
    '''automatically closes HWI client upon exit''' 
    device = get_device(device_id)
    client = get_client(device, network)
    try:
        yield client, device
    finally:
        client.close()

class ClientGroup:
    '''single "source of truth" for devices and clients'''

    def __init__(self):
        self.clients = []

    def send_pin(self, pin):
        for client in self.clients:
            success = client.send_pin(pin)['success']
        if success:
            self.close()
        return success

    def prompt_pin(self, network):
        devices = commands.enumerate()
        for device in devices:
            if device.get('needs_pin_sent'):
                client = get_client(device, network)
                client.prompt_pin()
                self.clients.append(client)

    def close(self):
        for client in self.clients:
            try:
                client.close()
                del client
            except:  # FIXME
                pass
        self.clients = []

###  Currency conversions

COIN_PER_SAT = Decimal(10) ** -8
SAT_PER_COIN = 100_000_000

def btc_to_sat(btc):
    return int(btc*SAT_PER_COIN)

def sat_to_btc(sat):
    return Decimal(sat/100_000_000).quantize(COIN_PER_SAT)

### Bitcoin Nodes

class RPC:

    def __init__(self, uri, timeout=30):
        self.uri = uri
        self.timeout = timeout
        self.rpc = AuthServiceProxy(self.uri, timeout=self.timeout)
        self.retries = 3

    def __getattr__(self, name):
        '''Retry failed RPC calls 3 times'''
        try:
            response = getattr(self.rpc, name)
            self.retries = 3
            return response
        except:
            if self.retries > 0:
                self.rpc = AuthServiceProxy(self.uri, timeout=self.timeout)
                self.retries -= 1
                return getattr(self, name)
            else:
                raise

    def test(self):
        '''raises JunctionErrors if RPC-connection doesn't work'''
        # Test RPC connection works
        try:
            self.getblockchaininfo()
        except (ConnectionRefusedError, http.client.CannotSendRequest) as e:
            raise JunctionError("ConnectionRefusedError: check https://bitcoin.stackexchange.com/questions/74337/testnet-bitcoin-connection-refused-111")
        except JSONRPCException as e:
            if "Unauthorized" in str(e):
                raise JunctionError("Please double-check your credentials!")

        # Check node version requirements are met
        version = self.getnetworkinfo()['version']
        if int(version) < 180000:
            raise JunctionError("Update your Bitcoin node to at least version 0.18")

        # Check wallet enabled
        try:
            self.getwalletinfo()
        except JSONRPCException as e:
            if "Method not found" in str(e):
                raise JunctionError("Junction requires 'disablewallet=0' in your bitcoin.conf")

        # Can't detect any problems
        return None

    def error(self):
        try:
            return self.test()
        except JunctionError as e:
            return str(e)

def default_bitcoin_datadir():
    datadir = None
    if sys.platform == 'darwin':
        datadir = os.path.join(os.environ['HOME'], "Library/Application Support/Bitcoin/")
    elif sys.platform == 'win32':
        datadir = os.path.join(os.environ['APPDATA'], "Bitcoin")
    else:
        datadir = os.path.join(os.environ['HOME'], ".bitcoin")
    return datadir

def default_bitcoin_conf():
    datadir = default_bitcoin_datadir()
    return os.path.join(datadir, 'bitcoin.conf')

def get_network_dir(datadir, network):
    network_to_folder_name = {
        "mainnet": "", 
        "testnet": "testnet3",
        "regtest": "regtest",
        "signet": "signet",
    }
    folder_name = network_to_folder_name[network]
    return os.path.join(datadir, folder_name)

def read_cookie(datadir, network):
    if datadir is None:
        datadir = default_bitcoin_datadir()
    network_dir = get_network_dir(datadir, network)
    cookie_path = os.path.join(network_dir, '.cookie')
    try:
        with open(cookie_path) as f:
            return f.read().split(':')
    except FileNotFoundError as e:
        logger.info("Could not read {} auto cookie".format(network))
        return None, None

def get_default_port(network):
    return {
        'mainnet': 8332,
        'testnet': 18332,
        'regtest': 18443,
    }[network]

def set_bitcoin_conf_default(config, network):
    config['rpcconnect'] = config.get('rpcconnect', 'localhost')
    config['rpcport'] = get_default_port(network)
    if 'rpcuser' not in config and 'rpcpassword' not in config:
        config['rpcuser'], config['rpcpassword'] = read_cookie(None, network)

def get_nodes():
    from junction import Node

    datadir = default_bitcoin_datadir()
    # Figure out the path to the bitcoin.conf file
    btc_conf_file = default_bitcoin_conf()

    # Bitcoin Core accepts empty rpcuser, not specified in btc_conf_file
    # default = {'rpcuser': ""}
    default = {}
    mainnet = {}
    testnet = {}
    regtest = {}
    current = default

    # Extract contents of bitcoin.conf to build service_url
    try:
        with open(btc_conf_file, 'r') as fd:
            for line in fd.readlines():
                if '#' in line:
                    line = line[:line.index('#')]
                if '[main]' in line:
                    current = mainnet
                    continue
                if '[test]' in line:
                    current = testnet
                    continue
                if '[regtest]' in line:
                    current = regtest
                    continue
                if '=' not in line:
                    continue
                k, v = line.split('=', 1)
                current[k.strip()] = v.strip()

    # Treat a missing bitcoin.conf as though it were empty
    except FileNotFoundError:
        pass

    # update network-specific configs with default config
    mainnet.update(default)
    testnet.update(default)
    regtest.update(default)

    # Return all nodes that are online
    nodes = []
    for config, network in [(mainnet, 'mainnet'), (regtest, 'regtest'), (testnet, 'testnet')]:
        set_bitcoin_conf_default(config, network)
        node = Node(
            host=config['rpcconnect'],
            port=config['rpcport'],
            user=config['rpcuser'],
            password=config['rpcpassword'],
            network=network,
            wallet_name=None,  # FIXME
        )
        try:
            node.default_rpc.test()
            node.running = True  # FIXME
            nodes.append(node)
        except:
            node.running = False
            pass
    return nodes

### Bitcoin scripts & addresses

def derive_child_sec_from_xpub(xpub, path):
    child_xpub = bip32.derive(xpub, path)
    child_xpub_bytes = base58.decode_check(child_xpub)
    # assertion about length?
    child_sec_bytes = child_xpub_bytes[-33:]
    child_sec_hex = child_sec_bytes.hex()
    return child_sec_hex