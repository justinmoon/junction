import json
from os import listdir
import os.path
from decimal import Decimal
from flask import flash, current_app as app
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from hwilib import commands
from hwilib.devices import coldcard, digitalbitbox, ledger, trezor

class JunctionError(Exception):
    pass

class JunctionWarning(Exception):
    pass

### HWI

def get_client_and_device(fingerprint):
    # get device
    devices = commands.enumerate()
    device = None
    for d in devices:
        if d.get('fingerprint') == fingerprint:
            device = d
    assert device is not None

    # get client
    if device['type'] == 'ledger':
        client = ledger.LedgerClient(device['path'])
    elif device['type'] == 'coldcard':
        client = coldcard.ColdcardClient(device['path'])
    elif device['type'] == 'trezor':
        client = trezor.TrezorClient(device['path'])
    else:
        raise JunctionError(f'Devices of type "{device["type"]}" not yet supported')
    client.is_testnet = True

    return client, device

### Flask

def flash_success(msg):
    flash(msg, 'success')

def flash_error(msg):
    flash(msg, 'danger')
    
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

    def __init__(self, settings, wallet_name=''):
        self.uri = self.uri_template.format(
            user=settings['rpc_username'],
            password=settings['rpc_password'], 
            host=settings['rpc_host'], 
            port=settings['rpc_port'], 
            wallet_name=wallet_name
        )

    def __getattr__(self, name):
        '''Create new proxy for every call to prevent timeouts'''
        rpc = AuthServiceProxy(self.uri, timeout=60)  # 1 minute timeout
        return getattr(rpc, name)

    def test(self):
        '''TODO: move test_rpc logic in here'''
        raise NotImplementedError()

def test_rpc(settings):
    ''' raises JunctionErrors or Warnings if RPC-connection doesn't work'''
    rpc = RPC(settings=settings)
    try:
        rpc.getblockchaininfo()
        if int(rpc.getnetworkinfo()['version']) < 170000:
           raise JunctionWarning("Update your Bitcoin Node to at least version > 0.17 otherwise this won't work.") 
        rpc.listwallets()
    except ConnectionRefusedError as e:
        raise JunctionError("ConnectionRefusedError: check https://bitcoin.stackexchange.com/questions/74337/testnet-bitcoin-connection-refused-111")
    except JSONRPCException as e:
        if "Unauthorized" in str(e):
            raise JunctionError("Please double-check your credentials!")
        elif "Method not found" in str(e):
            raise JunctionWarning("Make sure to have 'disablewallet=0' in your bitcoin.conf otherwise this won't work")
        else:
            handle_exception(e)
        return False 
    except Exception as e:
        app.logger.error("rpc-settings: {}".format(settings))
        handle_exception(e)
        raise JunctionError(e)
