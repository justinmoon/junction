from flask import Flask, render_template, jsonify
from hwilib import commands

app = Flask(__name__)

@app.route('/')
def index():
    devices = commands.enumerate()
    return render_template('index.html', devices=str(devices))

@app.route('/devices')
def devices():
    devices = commands.enumerate()
    return jsonify(devices)


