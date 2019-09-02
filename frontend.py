import json
import os
from flask import Flask, render_template, jsonify
from hwilib import commands
import logging

# FIXME: I should have 1 blueprint and prod + dev apps that register diff directoreis
# import os, sys
# if getattr(sys, 'frozen', False):
    # print('frozen')
    # app = Flask(
        # __name__,
        # static_folder=os.path.join(sys._MEIPASS, 'build/static')
        # template_folder=os.path.join(sys._MEIPASS, 'build')
    # )
# else:
    # print('not frozen')
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.info(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build/static'))
logger.info(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build'))
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build/static'),
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build'),
)

# @app.route("/")
# def hello():
    # return render_template('index.html')

@app.route("/path")
def path():
    return str(path.join(os.path.dirname(os.path.abspath(__file__)), 'build/static'))

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

