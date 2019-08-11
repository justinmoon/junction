import json
from pprint import pformat
from flask import Flask, render_template, jsonify
from hwilib import commands

from junction import MultiSig, bitcoin_rpc

app = Flask(__name__)

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

@app.route('/api/devices')
def devices():
    devices = commands.enumerate()
    return jsonify(devices)
