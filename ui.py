import json
from os.path import isfile
from pprint import pformat
from flask import Flask, render_template, jsonify, request, redirect, flash, url_for
from hwilib import commands
from utils import read_json_file, write_json_file, test_rpc

from junction import MultiSig, bitcoin_rpc

app = Flask(__name__)
app.secret_key = 'fixme'  # requied to flash messages for some reason ...

@app.before_request
def onboarding(): 
    endpoint = request.endpoint

    # ignore static folder
    if endpoint == 'static': 
        return

    # onboarding
    # step 1: settings
    if not isfile('settings.json') and endpoint != 'settings':
        return redirect(url_for('settings'))
    # step 2: create wallet
    elif not isfile('wallet.json') and endpoint != 'create_wallet':
        return redirect(url_for('create_wallet'))
    # now they can use other features

@app.route('/')
def index():
    devices = commands.enumerate()
    return render_template('index.html', devices=str(devices))

@app.route('/create-wallet')
def create_wallet():
    return render_template('create-wallet.html')

@app.route('/wallet')
def wallet():
    wallet = MultiSig.open('wallet.json')
    psbt = bitcoin_rpc.decodepsbt(wallet.psbt.serialize())
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
