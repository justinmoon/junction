import json
import logging
from os import listdir
import os.path
from decimal import Decimal
from flask import flash, current_app as app
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from hwilib import commands
from hwilib.devices import coldcard, digitalbitbox, ledger, trezor
from urllib import parse

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

def get_client(device):
    if device['type'] == 'ledger':
        client = ledger.LedgerClient(device['path'])
    elif device['type'] == 'coldcard':
        client = coldcard.ColdcardClient(device['path'])
    elif device['type'] == 'trezor':
        client = trezor.TrezorClient(device['path'])
    else:
        raise JunctionError(f'Devices of type "{device["type"]}" not yet supported')
    # FIXME: junction needs mainnet / testnet flag somewhere ...
    client.is_testnet = True
    return client

def get_client_and_device(path_or_fingerprint):
    for device in commands.enumerate():
        # TODO: maybe accept path or fingerprint?
        if device.get('path') == path_or_fingerprint:
            return get_client(device), device
        if device.get('fingerprint') == path_or_fingerprint:
            return get_client(device), device
    raise JunctionError(f'Device not found')

###  Currency conversions

COIN_PER_SAT = Decimal(10) ** -8
SAT_PER_COIN = 100_000_000

def btc_to_sat(btc):
    return int(btc*SAT_PER_COIN)

def sat_to_btc(sat):
    return Decimal(sat/100_000_000).quantize(COIN_PER_SAT)

### RPC

class RPC:

    uri_template = "http://{user}:{password}@{host}:{port}/wallet/{wallet_name}"

    def __init__(self, rpc_settings, wallet_name=''):
        self.uri = self.uri_template.format(**rpc_settings, wallet_name=parse.quote(wallet_name))

    def __getattr__(self, name):
        '''Create new proxy for every call to prevent timeouts'''
        rpc = AuthServiceProxy(self.uri, timeout=60)  # 1 minute timeout
        return getattr(rpc, name)

    def test(self):
        '''raises JunctionErrors if RPC-connection doesn't work'''
        try:
            self.getblockchaininfo()
            if int(self.getnetworkinfo()['version']) < 170000:
               raise JunctionWarning("Update your Bitcoin Node to at least version > 0.17 otherwise this won't work.") 
        except ConnectionRefusedError as e:
            raise JunctionError("ConnectionRefusedError: check https://bitcoin.stackexchange.com/questions/74337/testnet-bitcoin-connection-refused-111")
        except JSONRPCException as e:
            if "Unauthorized" in str(e):
                raise JunctionError("Please double-check your credentials!")
            elif "Method not found" in str(e):
                raise JunctionError("Make sure to have 'disablewallet=0' in your bitcoin.conf otherwise this won't work")
            else:
                raise JunctionError(e)
            return False 
        except Exception as e:
            logger.error("rpc-settings: {}".format(settings))
            raise JunctionError(e)
