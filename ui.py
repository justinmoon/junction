import json
import os
from os.path import isfile
from pprint import pformat, pprint
from flask import Flask, render_template, jsonify, request, redirect, flash, url_for
from hwilib import commands, serializations
from hwilib.devices import coldcard, digitalbitbox, ledger, trezor
from utils import read_json_file, write_json_file, test_rpc, wallets_exist, get_first_wallet_name

from junction import MultiSig, bitcoin_rpc, JunctionError

app = Flask(__name__)
app.secret_key = b'fixme'  # requied to flash messages for some reason ...

# global variable for bitbox password
bitbox_password = None
# global variable for TrezorClient instance. You must prompt and send pin with same instance
trezor_client = None


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
    # now they can use other features

@app.route('/')
def index():
    devices = commands.enumerate(bitbox_password)
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
        return redirect('http://localhost:5000/wallet')

@app.route('/create-psbt', methods=['POST'])
def create_psbt():
    wallet_name = get_first_wallet_name()
    multisig = MultiSig.open(wallet_name)
    multisig.create_psbt(request.form['recipient'], request.form['amount'])
    return redirect(url_for('wallet'))

@app.route('/wallet')
def wallet():
    wallet_name = get_first_wallet_name()
    wallet = MultiSig.open(wallet_name)

    devices = commands.enumerate(bitbox_password)
    pprint(devices)
    fingerprints = [device.get('fingerprint') for device in devices]
    for signer in wallet.signers:
        if signer['fingerprint'] in fingerprints:
            signer['device_state'] = 'unlocked'
        else:
            signer['device_state'] = 'unavailable'

    # FIXME
    if wallet.psbt:
        psbt = bitcoin_rpc.decodepsbt(wallet.psbt.serialize())
    else:
        psbt = None
    psbt_str = pformat(psbt)
    # signer_to_signed = {}
    # for signer in wallet.signers:
        # for deriv in psbt['bip32_derivs']:
            # if deriv['master_fingerprint'] == signer.fingerprint:
                # signer_to_signed[signer.name] = 
    return render_template('wallet.html', devices=devices, wallet=wallet, psbt=psbt, psbt_str=psbt_str)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # load settings if it exist, copy example file if it doesn't
    if isfile('settings.json'):
        settings = read_json_file("settings.json")
    else:
        settings = read_json_file('settings.json.ex')

    # handle requests
    if request.method == 'POST':
        # FIXME: attempt to exercise RPC with these settings
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
    flash(f'{multisig.name} signed successfully', 'success')
    return redirect(url_for('wallet'))

def get_client_and_device(fingerprint):
    # get device
    devices = commands.enumerate(bitbox_password)
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
    # maybe make a global password map for bitbox? it just stays in memory for each session ...
    elif device['type'] == 'digitalbitbox':
        client = digitalbitbox.DigitalbitboxClient(device['path'], bitbox_password)
    # elif device['type'] == 'trezor':
        # client = trezor.TrezorClient(device['path'])
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
    master_xpub = client.get_pubkey_at_path('m/0h')['xpub']
    origin_path = "m/44h/1h/0h"
    base_key = client.get_pubkey_at_path(origin_path)['xpub']
    multisig.add_signer(device['type'], device['fingerprint'], base_key, origin_path)
    flash(f"Signer \"{device['type']}\" has been added to your \"{multisig.name}\" wallet", 'success')

    # return to wallet page
    return redirect(url_for('wallet'))

@app.route('/api/devices')
def devices():
    devices = commands.enumerate(bitbox_password)
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

@app.route('/unlock', methods=['GET', 'POST'])
def unlock():
    global bitbox_password
    if request.method == 'GET':
        devices = commands.enumerate(bitbox_password)

        # prompt pins
        for device in devices:
            if device.get('needs_pin_sent'):
                # HACK
                global trezor_client
                trezor_client = trezor.TrezorClient(device['path'])
                trezor_client.prompt_pin()

        return render_template('unlock.html', devices=devices)
    else:
        print(request.form)
        if 'bitbox-password' in request.form:
            bitbox_password = request.form['bitbox-password']
        if 'trezor-1' in request.form:
            print(request.args)
            pin = ''
            next_digit = 1
            while len(pin) < 9:
                found = False
                for key, value in request.form.items():
                    print(value, next_digit)
                    if int(value) == next_digit:
                        place = key.split('-')[-1]
                        pin += place
                        next_digit += 1
                        found = True
                assert found, 'bad pin entry'
                print(repr(pin))
            devices = commands.enumerate(bitbox_password)
            for device in devices:
                if device['type'] == 'trezor':
                    print(device)
                    print(device['path'])
                    result = trezor_client.send_pin(pin)
                    del trezor_client
                    print(result)

        # Make sure bitbox password doesn't get into the query args ...
        # FIXME
        return redirect(url_for('unlock'))

if __name__ == '__main__':
    app.run(debug=True, threaded=False)
