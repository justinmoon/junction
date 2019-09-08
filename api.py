import logging

from flask import jsonify, request, redirect, url_for, Blueprint
from flask_json_schema import JsonSchema, JsonValidationError
from hwilib import commands

api = Blueprint(__name__, 'api')
schema = JsonSchema()
logger = logging.getLogger(__name__)

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
    'required': ['type', 'path'],
    'properties': {
        'type': { 'type': 'string' },
        'path':{ 'type': 'string' },
    },
})
def prompt_device():
    # set global TrezorClient instance
    raise NotImplementedError()

@api.route('/unlock', methods=['POST'])
@schema.validate({
    'properties': {
        'pin': { 'type': 'string' },  # trezor
        'password': { 'type': 'string' },  # bitbox
        'path':{ 'type': 'string' },
    },
})
def unlock_device():
    '''Prompt every device that's plugged in'''
    raise NotImplementedError()

@api.route('/wallets', methods=['GET'])
def list_wallets():
    # TODO: does this include addresses?
    raise NotImplementedError()

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
