import logging
import re

from flask import jsonify, request, redirect, url_for, Blueprint, current_app
from flask_json_schema import JsonSchema, JsonValidationError
from hwilib import commands, serializations
from hwilib.devices import trezor, ledger, coldcard

from junction import MultisigWallet, JunctionError
from disk import get_wallets, get_settings, update_settings, ensure_datadir
from utils import RPC, get_client_and_device, ClientGroup, get_device

import custom_coldcard
import custom_trezor

api = Blueprint(__name__, 'api')
schema = JsonSchema()
logger = logging.getLogger(__name__)
client_group = ClientGroup()

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
    }), 400

@api.before_request
def before_request():
    ensure_datadir()

@api.route('/devices', methods=['GET'])
def list_devices():
    return jsonify(commands.enumerate())

@api.route('/prompt', methods=['POST'])
def prompt_device():
    client_group.close()
    client_group.prompt_pin()
    return jsonify({})  # FIXME: what to do here when there's nothing to return

@api.route('/prompt', methods=['DELETE'])
def destroy_client():
    '''Kill the persistent CLIENT required for Trezor PIN entry'''
    client_group.close()
    return jsonify({}), 200

@api.route('/unlock', methods=['POST'])
@schema.validate({
    'properties': {
        'pin': { 'type': 'string' },  # trezor
        'password': { 'type': 'string' },  # bitbox
    },
})
def unlock_device():
    '''Prompt every device that's plugged in'''
    # more validation
    pin = request.json.get('pin')
    password = request.json.get('password')

    # attempt to unlock device
    if pin:
        success = client_group.send_pin(pin)
    # elif password:
    #     success = client_group.send_password(password)
    else:
        raise Exception("'pin' or 'password' must be present")

    # respond
    if success:
        client_group.close()
        return jsonify({})  # FIXME
    else:
        raise Exception('Failed to unlock device')


@api.route('/wallets', methods=['GET'])
def list_wallets():
    # TODO: does this include addresses?
    wallets = get_wallets()
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
    return jsonify(wallet.to_dict(True))

@api.route('/signers', methods=['POST'])
@schema.validate({
    'required': ['wallet_name', 'signer_name', 'device_id'],
    'properties': {
        'wallet_name': { 'type': 'string' },
        'signer_name': { 'type': 'string' },
        # device_id is fingerprint or path
        'device_id': { 'type': 'string' },  # FIXME: regex
    },
})
def add_signer():
    wallet_name = request.json['wallet_name']
    signer_name = request.json['signer_name']
    device_id = request.json['device_id']
    wallet = MultisigWallet.open(wallet_name)
    with get_client_and_device(device_id) as (client, device):
        derivation_path = "m/48'/1'/0'/2'"  # FIXME segwit
        # FIXME: validate xpub/tpub?
        xpub = client.get_pubkey_at_path(derivation_path)['xpub']
        client.close()
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
    address = wallet.address(change=False)
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
        'psbt': wallet.psbts[-1].serialize(),
    })

@api.route('/psbt', methods=['DELETE'])
@schema.validate({
    'required': ['wallet_name', 'index'],
    'properties': {
        'wallet_name': { 'type': 'string' },
        'index': { 'type': 'number' },
    },
})
def abandon_psbt():
    pass

@api.route('/sign', methods=['POST'])
@schema.validate({
    'required': ['wallet_name', 'device_id', 'index'],
    'properties': {
        # TODO: how to identify a specific psbt? index in wallet.psbts? Do they always have txids?
        'wallet_name': { 'type': 'string' },
        'device_id': { 'type': 'string' },  # FIXME: regex
        'index': { 'type': 'number' },
    },
})
def sign_psbt():
    wallet_name = request.json['wallet_name']
    wallet = MultisigWallet.open(wallet_name)
    fingerprint = request.json['device_id']
    index = request.json['index']
    old_psbt = wallet.psbts[index]
    with get_client_and_device(fingerprint) as (client, device):
        raw_signed_psbt = client.sign_tx(old_psbt)['psbt']
    new_psbt = serializations.PSBT()
    new_psbt.deserialize(raw_signed_psbt)
    wallet.update_psbt(new_psbt, index)
    return jsonify({
        'psbt': new_psbt.serialize(),
    })

@api.route('/settings', methods=['GET'])
def get_settings_route():
    settings = get_settings()
    try:
        RPC(settings['rpc'], timeout=5).test()
    except Exception as e:
        settings['rpc']['error'] = str(e)
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
                'port': {'type': 'string'},
            },
        },
    },
})
def update_settings_route():
    settings = request.json
    try:
        RPC(settings['rpc'], timeout=5).test()
    except Exception as e:
        settings['rpc']['error'] = str(e)
    update_settings(settings)
    return jsonify(settings)

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
    'required': ['wallet_name', 'index'],
    'properties': {
        'wallet_name': { 'type': 'string' },
        'index': { 'type': 'number' },
    },
})
def broadcast():
    wallet_name = request.json['wallet_name']
    index = request.json['index']
    wallet = MultisigWallet.open(wallet_name)
    txid = wallet.broadcast(index)
    return jsonify({
        'txid': txid,
    })

@api.route('/display-address', methods=['POST'])
@schema.validate({
    'required': ['wallet_name', 'address', 'device_id'],
    'properties': {
        'wallet_name': { 'type': 'string' },
        'address': { 'type': 'string' },
        'device_id': { 'type': 'string' },
    },
})
def display_address():
    wallet_name = request.json['wallet_name']
    address = request.json['address']
    device_id = request.json['device_id']
    wallet = MultisigWallet.open(wallet_name)

    device = get_device(device_id)

    # Get redeem script & derivation paths from RPC
    address_info = wallet.wallet_rpc.getaddressinfo(address)
    redeem_script = address_info.get('hex')
    descriptor = address_info.get('desc')
    if not redeem_script or not descriptor:
        raise JunctionError('Unknown address')
    derivation_paths = re.findall(r'\[(.*?)\]', descriptor)

    if device['type'] == 'trezor':
        derivation_path = ''
        for path in derivation_paths:
            slash_index = path.index('/')
            path = 'm' + path[slash_index:]
            if derivation_path:
                assert derivation_path == path
            else:
                derivation_path = path
        custom_trezor.display_multisig_address(redeem_script, derivation_path, wallet.testnet, device)
    elif device['type'] == 'coldcard':
        custom_coldcard.display_multisig_address(redeem_script, derivation_paths, wallet.native_segwit)
    else:
        raise JunctionError(f'Devices of type "{device["type"]}" do not support multisig address display')
    return jsonify({
        'ok': True
    })