from flask import Flask, render_template, jsonify
from hwilib import commands

app = Flask(__name__)

@app.route('/')
def index():
    devices = commands.enumerate()
    return render_template('index.html', devices=str(devices))

@app.route('/create-wallet')
def create_wallet():
    return render_template('create-wallet.html')

@app.route('/api/devices')
def devices():
    devices = commands.enumerate()
    return jsonify(devices)
