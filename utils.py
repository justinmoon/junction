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

### io

def write_json_file(data, filename):
    with open(filename, 'w') as f:
        return json.dump(data, f, indent=4)

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

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


### wallets

def get_first_wallet_name():
    file_names = listdir('wallets')
    if not file_names:
        return None
    file_name = file_names[0]
    return file_name.split('.')[0]

### settings

def get_settings():
    if os.path.isfile('settings.json'):
        return read_json_file("settings.json")
    else:
        return read_json_file('settings.json.ex')

def update_settings(new_settings):
    settings = get_settings()
    settings.update(new_settings)
    write_json_file(settings, 'settings.json')

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

    wallet_template = "http://{rpc_username}:{rpc_password}@{rpc_host}:{rpc_port}/wallet/{wallet_name}"

    def __init__(self, wallet_name='', settings=None):
        if settings is None:
            settings = get_settings()
        self.uri = self.wallet_template.format(**settings, wallet_name=wallet_name)

    def __getattr__(self, name):
        '''Create new proxy for every call to prevent timeouts'''
        rpc = AuthServiceProxy(self.uri, timeout=60)  # 1 minute timeout
        return getattr(rpc, name)

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

### ColdCard

# FIXME: do this with hwilib.devices.coldcard
# `real_file_upload` is the only thing that's missing
from utils import get_first_wallet_name
from ckcc.cli import ColdcardDevice, real_file_upload, MAX_BLK_LEN, CCProtocolPacker
from io import BytesIO

multisig_header = \
"""Name: {name}
Policy: {m} of {n}
Derivation: {path}
Format: {format}

"""
multisig_key = "\n{fingerprint}: {xpub}"

def coldcard_multisig_file(wallet):
    name = wallet.name[:20]  # 20 character max
    contents = multisig_header.format(name=name, m=wallet.m, n=wallet.n, 
                                      path="m/44'/1'/0'", format='P2SH')
    for signer in wallet.signers:
        contents += multisig_key.format(fingerprint=signer['fingerprint'],
                                        xpub=signer['xpub'])

    return BytesIO(contents.encode())

def coldcard_enroll(wallet):
    multisig_file = coldcard_multisig_file(wallet)

    force_serial = None
    dev = ColdcardDevice(sn=force_serial)

    file_len, sha = real_file_upload(multisig_file, MAX_BLK_LEN, dev=dev)

    dev.send_recv(CCProtocolPacker.multisig_enroll(file_len, sha))

def handle_exception(exception, user=None):
    ''' prints the exception and most important the stacktrace '''
    app.logger.error("Unexpected error")
    app.logger.error("----START-TRACEBACK-----------------------------------------------------------------")
    app.logger.exception(exception)    # the exception instance
    app.logger.error("----END---TRACEBACK-----------------------------------------------------------------")