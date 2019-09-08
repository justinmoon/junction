import logging

from flask import jsonify, request, redirect, url_for, Blueprint
from flask_json_schema import JsonSchema, JsonValidationError
from hwilib import commands
from hwilib.devices import trezor, ledger, coldcard

import disk

api = Blueprint(__name__, 'api')
schema = JsonSchema()
logger = logging.getLogger(__name__)
CLIENT = None

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

def get_client_and_device(path):
    for device in commands.enumerate():
        # TODO: maybe accept path or fingerprint?
        if device.get('path') == path:
            return get_client(device), device
    raise JunctionError(f'Device with path {path} not found')

@api.errorhandler(Exception)
def handle_unexpected_error(error):
    status_code = 500
    response = {
        'error': str(error)
    }
    logger.exception(error)
    return jsonify(response), status_code

@api.errorhandler(JsonValidationError)
def handle_validation_error(e):
    return jsonify({
        'error': e.message,
        'errors': [validation_error.message for validation_error  in e.errors],
    })

@api.route('/devices', methods=['GET'])
def list_devices():
    return jsonify(commands.enumerate())

@api.route('/prompt', methods=['POST'])
@schema.validate({
    'required': ['path'],
    'properties': {
        'path':{ 'type': 'string' },
    },
})
def prompt_device():
    global CLIENT
    path = request.json['path']
    client, device = get_client_and_device(path)
    if device.get('needs_pin_sent'):
        CLIENT = client
        client.prompt_pin()
    elif device.get('needs_password_sent'):
        # TODO this is for bitbox. not sure how to implement ...
        raise NotImplementedError()
    else:
        raise Exception(f'Device with path {device["path"]} already unlocked')
    return jsonify({})  # FIXME: what to do here when there's nothing to return

@api.route('/unlock', methods=['POST'])
@schema.validate({
    'required': ['path'],
    'properties': {
        'pin': { 'type': 'string' },  # trezor
        'password': { 'type': 'string' },  # bitbox
        'path':{ 'type': 'string' },
    },
})
def unlock_device():
    '''Prompt every device that's plugged in'''
    # more validation
    pin = request.json.get('pin')
    password = request.json.get('password')
    assert pin or password   # FIXME do in json schema

    # unlock device and return response
    global CLIENT
    result = CLIENT.send_pin(pin)
    if result['success']:
        del CLIENT
        return jsonify({})  # FIXME
    else:
        raise Exception('Failed to unlock device')


@api.route('/wallets', methods=['GET'])
def list_wallets():
    # TODO: does this include addresses?
    wallets = disk.get_wallets()
    # FIXME: probably shouldn't include xpubs in this response?
    wallet_dicts = [wallet.to_dict() for wallet in wallets]
    return jsonify(wallet_dicts)

@api.route('/wallets', methods=['POST'])
@schema.validate({
    'required': ['name', 'm', 'n'],
    'properties': {
        'name': { 'type': 'string' },
        'm': { 'type': 'integer' },
        'n': { 'type': 'integer' },
    },
})
def create_wallet():
    raise NotImplementedError()

@api.route('/signers', methods=['POST'])
@schema.validate({
    'required': ['wallet', 'fingerprint'],
    'properties': {
        'wallet': { 'type': 'string' },
        'fingerprint': { 'type': 'string' },  # FIXME: regex
    },
})
def add_signer(wallet_name):
    raise NotImplementedError()

@api.route('/addresses', methods=['POST'])
@schema.validate({
    'required': ['wallet', 'fingerprint'],
    'properties': {
        'wallet': { 'type': 'string' },
        'fingerprint': { 'type': 'string' },  # FIXME: regex
    },
})
def generate_address(wallet_name):
    raise NotImplementedError()

@api.route('/psbt', methods=['GET'])
def list_psbt():
    raise NotImplementedError()

@api.route('/psbt', methods=['POST'])
@schema.validate({
    'required': ['outputs', 'wallet'],
    'properties': {
        # todo: inputs, feerate, rbf, etc
        'wallet': 'string',
        'outputs': {
            'type': 'array',
            'items': {
                'required': ['recipient', 'amount'],
                'properties': {
                    'recipient': { 'type': 'address' },   # FIXME: regex
                    # TODO: assume btc if decimal, satoshis if not?
                    'amount': { 'type': 'integer' },      # FIXME: regex
                },
            },
        },
    },
})
def create_psbt():
    raise NotImplementedError()

@api.route('/sign', methods=['POST'])
@schema.validate({
    'required': ['txid', 'fingerprint'],
    'properties': {
        # FIXME: is this sufficient for legacy transactions? 
        'txid': { 'type': 'string' },  # FIXME: regex
        'fingerprint': { 'type': 'string' },  # FIXME: regex
    },
})
def sign_psbt():
    raise NotImplementedError()

@api.route('/settings', methods=['GET'])
def get_settings():
    raise NotImplementedError()

@api.route('/settings', methods=['PUT'])
def update_settings():
    raise NotImplementedError()

@api.route('/utxos', methods=['GET'])
def list_utxos():
    # FIXME: display utxos across all wallets, or per-wallet?
    raise NotImplementedError()

@api.route('/transactions', methods=['GET'])
def list_transactions():
    # FIXME: display transactions across all wallets, or per-wallet?
    raise NotImplementedError()

@api.route('/broadcast', methods=['POST'])
@schema.validate({
    'required': ['txid'],
    'properties': {
        'txid': { 'type': 'string' },  # FIXME: regex
    },
})
def broadcast_transaction():
    raise NotImplementedError()
