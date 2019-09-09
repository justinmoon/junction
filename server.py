from hwilib import commands
from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify(commands.enumerate())

@app.route('/enumerate')
def enumerate():
    return jsonify(commands.enumerate())

@app.route('/psbt')
def psbt():
    with open('data/psbt_decoded.json'):
        data = json.load(json_file)
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
