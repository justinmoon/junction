import json
import os
from os.path import isfile
from pprint import pformat, pprint
from flask import Flask, render_template, jsonify, request, redirect, url_for
from hwilib import commands, serializations
from hwilib.devices import trezor
from utils import read_json_file, write_json_file, test_rpc, get_first_wallet_name, btc_to_sat, JSONRPCException, coldcard_enroll, flash_success, flash_error, update_settings, get_client_and_device, get_settings
from junction import MultisigWallet, JunctionError

app = Flask(__name__)
app.secret_key = b'orangecoingood'  # flashed messages stored on session

# global variable for TrezorClient instance b/c you must prompt and send pin with same instance
trezor_client = None
wallet_name = get_first_wallet_name()

@app.errorhandler(JunctionError)
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
    elif not wallet_name:
        if endpoint != 'create_wallet':
            return redirect(url_for('create_wallet'))

@app.route('/enumerate')
def enumerate():
    devices = json.dumps(commands.enumerate(), indent=4)
    return render_template('enumerate.html', devices=devices)

@app.route('/api/enumerate')
def api_enumerate():
    return jsonify(commands.enumerate())

@app.route('/create-wallet', methods=['GET', 'POST'])
def create_wallet():
    global wallet_name
    if request.method == 'GET':
        return render_template('create-wallet.html')
    else:
        try:
            wallet_name = request.form['name']
            m = int(request.form['m'])
            n = int(request.form['n'])
            MultisigWallet.create(wallet_name, m, n)
            flash_success('Wallet created')
        except JunctionError as e:
            flash_error(str(e))
            return render_template('create-wallet.html')
        return redirect(url_for('wallet'))

@app.route('/create-psbt', methods=['POST'])
def create_psbt():
    wallet = MultisigWallet.open(wallet_name)
    wallet.create_psbt(request.form['recipient'], int(request.form['satoshis']))
    return redirect(url_for('wallet'))

@app.route('/')
def wallet():
    wallet = MultisigWallet.open(wallet_name)
    devices = commands.enumerate()
    unconfirmed_balance, confirmed_balance = wallet.balances()

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

    # FIXME: ugly
    for signer in wallet.signers:
        match = {'error': "Not found"}  # note: "Not found" is used in UI
        for device in devices:
            if device.get('fingerprint') == signer['fingerprint']:
                match = device
        signer['device'] = match

    # FIXME: ugly
    signer_fingerprints = [signer['fingerprint'] for signer in wallet.signers]
    potential_signers = [d for d in devices if 'fingerprint' not in d
            or d['fingerprint'] not in signer_fingerprints]

    return render_template('wallet.html', devices=devices, wallet=wallet, psbt=psbt,
            unconfirmed_balance=unconfirmed_balance, confirmed_balance=confirmed_balance,
            potential_signers=potential_signers, btc_to_sat=btc_to_sat)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        rpc_settings = dict(request.form)
        if test_rpc(rpc_settings):
            update_settings(rpc_settings)
            flash_success('Settings updated')
            return redirect(url_for('wallet'))
        else:
            flash_error('Invalid settings')
            return redirect(url_for('settings'))
    else:
        settings = get_settings()
        return render_template("settings.html", settings=settings)


@app.route('/sign-psbt/<fingerprint>', methods=['POST'])
def sign_psbt(fingerprint):
    wallet = MultisigWallet.open(wallet_name)
    client, device = get_client_and_device(fingerprint)
    psbt = wallet.psbt
    raw_signed_psbt = client.sign_tx(wallet.psbt)['psbt']
    new_psbt = serializations.PSBT()
    new_psbt.deserialize(raw_signed_psbt)
    wallet.psbt = new_psbt
    wallet.save()
    # FIXME: display the signer name here ...
    flash_success(f'{device["type"]} signed successfully')
    return redirect(url_for('wallet'))

@app.route('/add-signer/<fingerprint>', methods=['POST'])
def add_signer(fingerprint):
    wallet = MultisigWallet.open(wallet_name)
    client, device = get_client_and_device(fingerprint)

    # Add a "signer" to the wallet
    account_path = "m/44h/1h/0h"
    base_key = client.get_pubkey_at_path(account_path)['xpub']
    wallet.add_signer(device['type'], device['fingerprint'], base_key, account_path)

    # FIXME: only works when coldcard added last
    if device['type'] == 'coldcard':
        client.close()
        coldcard_enroll(wallet)

    msg = f"Signer \"{device['type']}\" has been added to your \"{wallet.name}\" wallet"
    flash_success(msg)

    return redirect(url_for('wallet'))

@app.route('/api/devices')
def api_devices():
    devices = commands.enumerate()
    return jsonify(devices)

@app.route('/export')
def export():
    wallet = MultisigWallet.open(wallet_name)
    wallet.export_watchonly()
    return redirect(url_for('wallet'))

@app.route('/address')
def address():
    wallet = MultisigWallet.open(wallet_name)
    address = wallet.address()
    return address, 200

@app.route('/broadcast', methods=['POST'])
def broadcast():
    wallet = MultisigWallet.open(wallet_name)
    wallet.broadcast()
    wallet.remove_psbt()
    wallet.save()
    flash_success('transaction broadcasted successfully')
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
    return redirect(url_for('devices'))

@app.route('/devices')
def devices():
    devices = commands.enumerate()

    # prompt pins
    for device in devices:
        if device.get('needs_pin_sent'):
            global trezor_client
            trezor_client = trezor.TrezorClient(device['path'])
            trezor_client.prompt_pin()

    everything_unlocked = not any(['error' in device for device in devices])

    return render_template('devices.html', devices=devices, everything_unlocked=everything_unlocked)

if __name__ == '__main__':
    # FIXME: hack to prevent unloaded wallet
    try:
        wallet = MultisigWallet.open(wallet_name)
        wallet.ensure_watchonly()
    except:
        pass

    # Run flask, kill bitcoind on ctrl-c
    try:
        app.run(debug=True, threaded=False)
    except KeyboardInterrupt:
        process.terminate()
        print()

