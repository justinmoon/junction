import logging

from flask import jsonify, request, redirect, url_for, Blueprint
from flask_json_schema import JsonSchema, JsonValidationError
from hwilib import commands, serializations
from hwilib.devices import trezor, ledger, coldcard

from junction import MultisigWallet, JunctionError
import disk
from utils import RPC

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

def get_client_and_device(path_or_fingerprint):
    for device in commands.enumerate():
        # TODO: maybe accept path or fingerprint?
        if device.get('path') == path_or_fingerprint:
            return get_client(device), device
        if device.get('fingerprint') == path_or_fingerprint:
            return get_client(device), device
    raise JunctionError(f'Device not found')

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
    wallet_dicts = [wallet.to_dict(True) for wallet in wallets]
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
    wallet = MultisigWallet.create(**request.json)
    return jsonify({})  # FIXME

@api.route('/signers', methods=['POST'])
@schema.validate({
    'required': ['wallet_name', 'signer_name', 'fingerprint'],
    'properties': {
        'wallet_name': { 'type': 'string' },
        'signer_name': { 'type': 'string' },
        # FIXME: or path???
        'fingerprint': { 'type': 'string' },  # FIXME: regex
    },
})
def add_signer():
    wallet_name = request.json['wallet_name']
    signer_name = request.json['signer_name']
    fingerprint = request.json['fingerprint']
    wallet = MultisigWallet.open(wallet_name)
    client, device = get_client_and_device(fingerprint)
    derivation_path = "m/44h/1h/0h"  # FIXME segwit
    # FIXME: validate xpub/tpub?
    xpub = client.get_pubkey_at_path(derivation_path)['xpub']
    wallet.add_signer(name=signer_name, fingerprint=device['fingerprint'], type=device['type'], xpub=xpub, derivation_path=derivation_path)
    return jsonify(wallet.to_dict())

@api.route('/address', methods=['POST'])
@schema.validate({
    'required': ['wallet_name'],
    'properties': {
        'wallet_name': { 'type': 'string' },
    },
})
def address():
    # TODO: it would be better to generate addresses ahead of time and store them on the wallet
    # just not sure how to implement that
    wallet_name = request.json['wallet_name']
    wallet = MultisigWallet.open(wallet_name)
    address = wallet.address()
    return jsonify({
        'address': address,
    })

@api.route('/psbt', methods=['POST'])
@schema.validate({
    'required': ['outputs'],
    'properties': {
        'wallet_name': {'type': 'string'},
        # todo: inputs, feerate, rbf, etc
        'outputs': {
            'type': 'array',
            'items': {
                'required': ['address', 'btc'],
                'properties': {
                    'address': {'type': 'string'},   # FIXME: regex
                    'btc': {'type': 'number'},      # FIXME: regex
                    # 'satoshis': {'type': 'integer'},      # FIXME: regex
                },
            },
        },
    },
})
def create_psbt():
    wallet_name = request.json['wallet_name']
    wallet = MultisigWallet.open(wallet_name)
    outputs = []
    for output in request.json['outputs']:
        output_dict = {output['address']: output['btc']}
        outputs.append(output_dict)
    wallet.create_psbt(outputs)
    return jsonify({
        'psbt': wallet.psbt.serialize(),
    })

@api.route('/sign', methods=['POST'])
@schema.validate({
    'required': ['wallet_name', 'fingerprint'],
    'properties': {
        # TODO: how to identify a specific psbt? index in wallet.psbts? Do they always have txids?
        'wallet_name': { 'type': 'string' },
        'fingerprint': { 'type': 'string' },  # FIXME: regex
    },
})
def sign_psbt():
    wallet_name = request.json['wallet_name']
    wallet = MultisigWallet.open(wallet_name)
    fingerprint = request.json['fingerprint']
    client, device = get_client_and_device(fingerprint)
    raw_signed_psbt = client.sign_tx(wallet.psbt)['psbt']
    new_psbt = serializations.PSBT()
    new_psbt.deserialize(raw_signed_psbt)
    wallet.update_psbt(new_psbt)
    return jsonify({
        'psbt': wallet.psbt.serialize(),
    })

@api.route('/settings', methods=['GET'])
def get_settings():
    settings = disk.get_settings()
    return jsonify(settings)

@api.route('/settings', methods=['PUT'])
@schema.validate({
    'required': ['rpc'],
    'properties': {
        'rpc': {
            'required': ['user', 'password', 'host', 'port'],
            'properties': {
                'user': {'type': 'string'},
                'password': {'type': 'string'},
                'host': {'type': 'string'},
                'port': {'type': 'integer'},
            },
        },
    },
})
def update_settings():
    settings = request.json
    RPC(settings['rpc']).test()
    disk.update_settings(settings)
    return jsonify({})

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
    'required': ['wallet_name'],
    'properties': {
        'wallet_name': { 'type': 'string' },
    },
})
def broadcast():
    wallet_name = request.json['wallet_name']
    wallet = MultisigWallet.open(wallet_name)
    txid = wallet.broadcast()
    return jsonify({
        'txid': txid,
    })
