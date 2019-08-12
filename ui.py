import json
from os.path import isfile
from pprint import pformat
from flask import Flask, render_template, jsonify, request, redirect, flash, url_for
from hwilib import commands
from utils import read_json_file, write_json_file, test_rpc, wallets_exist, get_first_wallet_name

from junction import MultiSig, bitcoin_rpc, JunctionError

app = Flask(__name__)
app.secret_key = b'fixme'  # requied to flash messages for some reason ...

@app.before_request
def onboarding(): 
    endpoint = request.endpoint

    # ignore static folder
    if endpoint == 'static': 
        return

    # onboarding
    # step 1: settings
    print(isfile('settings.json'), endpoint)
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
    devices = commands.enumerate()
    return render_template('index.html', devices=str(devices))

@app.route('/create-wallet', methods=['GET', 'POST'])
def create_wallet():
    if request.method == 'GET':
        return render_template('create-wallet.html')
    else:
        try:
            MultiSig.create(**dict(request.form))
            flash('Wallet created', 'success')
        except JunctionError as e:
            flash(str(e), 'danger')
            return render_template('create-wallet.html')
        print(url_for('wallet'))
        return redirect('http://localhost:5000/wallet')

@app.route('/wallet')
def wallet():
    wallet_name = get_first_wallet_name()
    wallet = MultiSig.open(wallet_name)
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
    return render_template('wallet.html', wallet=wallet, psbt=psbt, psbt_str=psbt_str)

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

@app.route('/api/devices')
def devices():
    devices = commands.enumerate()
    return jsonify(devices)
