import logging
import re

from flask import jsonify, request, redirect, url_for, Blueprint, current_app
from flask_json_schema import JsonSchema, JsonValidationError
from hwilib import commands, serializations
from hwilib.devices import trezor, ledger, coldcard

from junction import MultisigWallet, JunctionError, Node
from disk import get_wallets, get_settings, update_settings, ensure_datadir
from utils import RPC, get_client_and_device, ClientGroup, get_device, get_nodes

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
@schema.validate({
    'properties': {
        'wallet_name': { 'type': 'string' },
    },
})
def prompt_device():
    client_group.close()
    wallet_name = request.json['wallet_name']
    wallet = MultisigWallet.open(wallet_name)
    client_group.prompt_pin(wallet.network)
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
    'required': ['name', 'm', 'n', 'network', 'node'],
    'properties': {
        'name': { 'type': 'string' },
        'm': { 'type': 'integer' },
        'n': { 'type': 'integer' },
        'network': { 'type': 'string' },
        'node': {
            'required': ['user', 'password', 'host', 'port'],
            'properties': {
                'user': { 'type': 'string' },
                'password': { 'type': 'string' },
                'host': { 'type': 'string' },
                'port': { 'type': 'string' },
            }
        }
    },
})
def create_wallet():
    node_args = request.json.pop('node')
    node = Node(**node_args, wallet_name=request.json['name'], 
                network=request.json['network'])
    # check that node is reachable
    node.default_rpc.test()
    wallet = MultisigWallet.create(**request.json, node=node)
    return jsonify(wallet.to_dict(True))

@api.route('/signers', methods=['POST'])
@schema.validate({
    'required': ['wallet_name', 'signer_name', 'device_id'],
    'properties': {
        'wallet_name': { 'type': 'string' },
        'signer_name': { 'type': 'string' },
        'device_id': { 'type': 'string' },
    },
})
def add_signer():
    wallet_name = request.json['wallet_name']
    signer_name = request.json['signer_name']
    device_id = request.json['device_id']
    wallet = MultisigWallet.open(wallet_name)
    with get_client_and_device(device_id, wallet.network) as (client, device):
        derivation_path = wallet.account_derivation_path()
        # Get XPUB and validate against wallet.network 
        xpub = client.get_pubkey_at_path(derivation_path)['xpub']
        if 'xpub' == xpub[:4] and wallet.network != 'mainnet':
            raise JunctionError('Invalid xpub. Make sure your device is set to the correct chain.')
        if 'tpub' == xpub[:4] and wallet.network == 'mainnet':
            raise JunctionError('Invalid xpub. Make sure your device is set to the correct chain.')
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
                'required': ['address', 'btc', 'subtract_fees'],
                'properties': {
                    'address': {'type': 'string'},   # FIXME: regex
                    'btc': {'type': 'number'},      # FIXME: regex
                    # 'satoshis': {'type': 'integer'},      # FIXME: regex
                    'subtract_fees': { 'type': 'boolean' }
                },
            },
        },
    },
})
def create_psbt():
    wallet_name = request.json['wallet_name']
    wallet = MultisigWallet.open(wallet_name)
    api_outputs = request.json['outputs']
    outputs = []
    for output in api_outputs:
        output_dict = {output['address']: output['btc']}
        outputs.append(output_dict)
    subtract_fees = [index for index, output in enumerate(api_outputs) 
                     if output['subtract_fees']]
    wallet.create_psbt(outputs, subtract_fees=subtract_fees)
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
    with get_client_and_device(fingerprint, wallet.network) as (client, device):
        raw_signed_psbt = client.sign_tx(old_psbt)['psbt']
    new_psbt = serializations.PSBT()
    new_psbt.deserialize(raw_signed_psbt)
    wallet.update_psbt(new_psbt, index)
    return jsonify({
        'psbt': new_psbt.serialize(),
    })

@api.route('/nodes')
def list_nodes():
    nodes = get_nodes()
    return jsonify({
        "bitcoin": [node.to_dict(True) for node in nodes],
        "lightning": [],
    })


@api.route('/nodes', methods=['PUT'])
@schema.validate({
    'required': ['wallet_name', 'user', 'password', 'host', 'port'],
    'properties': {
        'wallet_name': {'type': 'string'},
        'user': {'type': 'string'},
        'password': {'type': 'string'},
        'host': {'type': 'string'},
        'port': {'type': 'string'},
    },
})
def update_node():
    wallet_name = request.json['wallet_name']
    wallet = MultisigWallet.open(wallet_name)
    node_params = request.json
    node = Node(**node_params, wallet_name=wallet.name, network=wallet.network)
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

    address_info = wallet.node.wallet_rpc.getaddressinfo(address)
    descriptor = address_info.get('desc')

    # HWI doesn't cover multisig, so we have to cover separately
    if wallet.wallet_type == 'multi':
        # Get redeem script
        if wallet.script_type == 'native':
            redeem_script = address_info.get('hex')
        else:
            redeem_script = address_info.get('embedded', {}).get('hex')
        
        # Make sure we have redeem_script and descriptor
        if not redeem_script or not descriptor:
            raise JunctionError('Unknown address')

        # Grab derivation path portions of descriptor
        derivation_paths = re.findall(r'\[(.*?)\]', descriptor)

        # Handle Trezors
        if device['type'] == 'trezor':
            # FIXME: give descriptor to custom_trezor.display_multisig_address and have it do this ...
            derivation_path = ''
            for path in derivation_paths:
                slash_index = path.index('/')
                path = 'm' + path[slash_index:]
                if derivation_path:
                    assert derivation_path == path
                else:
                    derivation_path = path
           
            custom_trezor.display_multisig_address(redeem_script, derivation_path, wallet.network != 'mainnet', device, wallet.script_type)
        # Handle ColdCards
        elif device['type'] == 'coldcard':
            custom_coldcard.display_multisig_address(redeem_script, derivation_paths, wallet.script_type == 'native')
        # Reject everything else
        else:
            raise JunctionError(f'Devices of type "{device["type"]}" do not support multisig address display')
    # HWI covers single-sig
    else:
        with get_client_and_device(device_id, wallet.network) as (client, device):
            commands.displayaddress(client, desc=descriptor)
    
    return jsonify({
        'ok': True
    })

@api.route('/register-device', methods=['POST'])
@schema.validate({
    'required': ['wallet_name', 'device_id'],
    'properties': {
        'wallet_name': { 'type': 'string' },
        'device_id': { 'type': 'string' },
    },
})
def register_device():
    wallet_name = request.json['wallet_name']
    device_id = request.json['device_id']
    wallet = MultisigWallet.open(wallet_name)

    device = get_device(device_id)

    fingerprints = [signer.fingerprint for signer in wallet.signers]
    if device['fingerprint'] not in fingerprints:
        raise JunctionError(f'No device with fingerprint {device["fingerprint"]} present in wallet {wallet_name}')

    if device['type'] != 'coldcard':
        raise JunctionError(f'Devices of type {device["type"]} do not support multisig wallet registration')

    custom_coldcard.enroll(wallet)

    # TODO: How to keep track of whether or not this multisig wallet is registered on the coldcard?

    return jsonify({'ok': True})