from hwilib import commands
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(commands.enumerate())

if __name__ == '__main__':
    app.run()
