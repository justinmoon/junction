import json
from flask import Flask, render_template, jsonify
from hwilib import commands

app = Flask(
    __name__,
    static_folder="frontend/build/static",
    template_folder="frontend/build",
)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/enumerate")
def enumerate():
    return jsonify(commands.enumerate())

@app.route("/transactions")
def transactions():
    with open('data/listtransactions.json', 'r') as f:
        txns = json.load(f)[::-1]
    return jsonify(txns)

@app.route("/psbt")
def psbt():
    with open('data/psbt.json', 'r') as f:
        psbt = json.load(f)
    return jsonify(psbt)

