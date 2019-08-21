import json
import os
from os.path import isfile
from pprint import pformat, pprint
from flask import Flask, render_template, jsonify, request, redirect, flash, url_for
from hwilib import commands, serializations
from hwilib.devices import coldcard, digitalbitbox, ledger, trezor
from utils import read_json_file, write_json_file, test_rpc, wallets_exist, get_first_wallet_name, btc_to_sat, JSONRPCException, coldcard_enroll
from junction import MultiSig, bitcoin_rpc, JunctionError

app = Flask(__name__)
app.secret_key = b'orangecoingood'  # flashed messages stored on session

# global variable for TrezorClient instance b/c you must prompt and send pin with same instance
trezor_client = None

def flash_success(msg):
    flash(msg, 'success')

def flash_error(msg):
    flash(msg, 'danger')

@app.errorhandler(JSONRPCException)
def handle_rpc_exception(e):
    return "Error: {}".format(e)

@app.before_request
def onboarding(): 
    endpoint = request.endpoint

    # ignore static folder
    if endpoint == 'static': 
        return

    # onboarding
    # step 1: settings
    if not isfile('settings.json'):
        if endpoint != 'settings':
            return redirect(url_for('settings'))
    # step 2: create wallet
    elif not wallets_exist():
        if endpoint != 'create_wallet':
            return redirect(url_for('create_wallet'))

@app.route('/enumerate')
def enumerate():
    devices = commands.enumerate()
    return render_template('index.html', devices=str(devices))

@app.route('/create-wallet', methods=['GET', 'POST'])
def create_wallet():
    if request.method == 'GET':
        return render_template('create-wallet.html')
    else:
        try:
            name = request.form['name']
            # FIXME: for some reason these are strings ...
            m = int(request.form['m'])
            n = int(request.form['n'])
            MultiSig.create(name, m, n)
            flash('Wallet created', 'success')
        except JunctionError as e:
            flash(str(e), 'danger')
            return render_template('create-wallet.html')
        return redirect(url_for('wallet'))

@app.route('/create-psbt', methods=['POST'])
def create_psbt():
    wallet_name = get_first_wallet_name()
    multisig = MultiSig.open(wallet_name)
    multisig.create_psbt(request.form['recipient'], int(request.form['satoshis']))
    return redirect(url_for('wallet'))

@app.route('/')
def wallet():
    wallet_name = get_first_wallet_name()
    wallet = MultiSig.open(wallet_name)
    devices = commands.enumerate()
    unconfirmed, confirmed, spendable = wallet.balances()

    # FIXME: ugly
    if wallet.psbt:
        psbt = wallet.decode_psbt()
        pprint(psbt)
        for signer in wallet.signers:
            signed = False
            # FIXME: this should check they've signed every input, not just one input
            for input in psbt['inputs']:
                for deriv in input['bip32_derivs']:
                    fingerprint_match = deriv['master_fingerprint'] == signer['fingerprint']
                    pubkey_match = deriv['pubkey'] in input.get('partial_signatures', [])
                    if fingerprint_match and pubkey_match:
                        signed = True
            signer['signed'] = signed

    else:
        psbt = None

    # FIXME: 'signed' isn't always present
    signed = all([signer.get('signed') for signer in wallet.signers])

    # FIXME: ugly
    for signer in wallet.signers:
        match = {'error': "Not found"}  # note: "Not found" is used in UI
        for device in devices:
            if device.get('fingerprint') == signer['fingerprint']:
                match = device
        signer['device'] = match
    pprint(wallet.signers)

    # FIXME: ugly
    signer_fingerprints = [signer['fingerprint'] for signer in wallet.signers]
    potential_signers = [d for d in devices if 'fingerprint' not in d
            or d['fingerprint'] not in signer_fingerprints]
    print('potential signers')
    pprint(potential_signers)

    return render_template('wallet.html', devices=devices, wallet=wallet, psbt=psbt,
            spendable=spendable,
            potential_signers=potential_signers, confirmed=confirmed, unconfirmed=unconfirmed, signed=signed, btc_to_sat=btc_to_sat)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # load settings if it exist, copy example file if it doesn't
    if isfile('settings.json'):
        settings = read_json_file("settings.json")
    else:
        settings = read_json_file('settings.json.ex')

    # handle requests
    if request.method == 'POST':
        rpc_settings = dict(request.form)
        if test_rpc(rpc_settings):
            settings['rpc'] = dict(request.form)
            write_json_file(settings, 'settings.json') 
            flash('Settings updated', 'success')
            return redirect(url_for('wallet'))
        else:
            flash('Invalid settings', 'danger')
            return render_template("settings.html", settings=settings)
    else:
        return render_template("settings.html", settings=settings)


@app.route('/sign-psbt/<fingerprint>', methods=['POST'])
def sign_psbt(fingerprint):
    wallet_name = get_first_wallet_name()
    multisig = MultiSig.open(wallet_name)
    client, device = get_client_and_device(fingerprint)
    psbt = multisig.psbt
    raw_signed_psbt = client.sign_tx(multisig.psbt)['psbt']
    new_psbt = serializations.PSBT()
    new_psbt.deserialize(raw_signed_psbt)
    multisig.psbt = new_psbt
    multisig.save()
    # FIXME: display the signer name here ...
    flash(f'{device["type"]} signed successfully', 'success')
    return redirect(url_for('wallet'))

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

@app.route('/add-signer/<fingerprint>', methods=['POST'])
def add_signer(fingerprint):
    wallet_name = get_first_wallet_name()
    multisig = MultiSig.open(wallet_name)
    client, device = get_client_and_device(fingerprint)

    # Add a "signer" to the wallet
    account_path = "m/44h/1h/0h"
    base_key = client.get_pubkey_at_path(account_path)['xpub']
    multisig.add_signer(device['type'], device['fingerprint'], base_key, account_path)

    msg = f"Signer \"{device['type']}\" has been added to your \"{multisig.name}\" wallet."
    if device['type'] == 'coldcard':
        client.close()
        coldcard_enroll(multisig)
        msg += ' Please confirm on your ColdCard.'

    flash_success(msg)

    # return to wallet page
    return redirect(url_for('wallet'))

@app.route('/api/devices')
def devices():
    devices = commands.enumerate()
    return jsonify(devices)

@app.route('/export')
def export():
    wallet_name = get_first_wallet_name()
    multisig = MultiSig.open(wallet_name)
    multisig.export_watchonly()
    return redirect(url_for('wallet'))

@app.route('/address')
def address():
    wallet_name = get_first_wallet_name()
    multisig = MultiSig.open(wallet_name)
    address = multisig.address()
    return address, 200

@app.route('/broadcast', methods=['POST'])
def broadcast():
    wallet_name = get_first_wallet_name()
    multisig = MultiSig.open(wallet_name)
    multisig.broadcast()
    # FIXME: this is a little sketchy ...
    multisig.psbt = ''
    multisig.save()
    flash('transaction broadcasted successfully', 'success')
    return redirect(url_for('wallet'))

@app.route('/set-pin', methods=['POST'])
def set_pin():
    global trezor_client
    # construct pin
    pin = ''
    map = {v: k for k, v in request.form.items()}
    for k in sorted(map.keys()):
        pin += map[k]
    # test pin
    result = trezor_client.send_pin(pin)
    if result['success']:
        flash_success('Device unlocked')
        del trezor_client
    else:
        flash_error('Bad pin')
    return redirect(url_for('unlock'))

@app.route('/unlock')
def unlock():
    devices = commands.enumerate()

    # prompt pins
    for device in devices:
        if device.get('needs_pin_sent'):
            global trezor_client
            trezor_client = trezor.TrezorClient(device['path'])
            trezor_client.prompt_pin()

    everything_unlocked = not any(['error' in device for device in devices])

    return render_template('unlock.html', devices=devices, everything_unlocked=everything_unlocked)

@app.route('/display')
def display():
    wallet_name = get_first_wallet_name()
    multisig = MultiSig.open(wallet_name)
    devices = commands.enumerate()
    for device in devices:
        if device['type'] == 'trezor':
            client = trezor.TrezorClient(device['path'])
            res = commands.displayaddress(client, desc=multisig.descriptor())
            return str(res), 200
    return 'no trezor', 200

if __name__ == '__main__':
    try:
        wallet_name = get_first_wallet_name()
        multisig = MultiSig.open(wallet_name)
        # FIXME: hack to prevent unloaded wallet
        multisig.create_watchonly()
    except:
        pass
    app.run(debug=True, threaded=False)
