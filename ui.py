from flask import Flask, render_template
from hwilib import commands

app = Flask(__name__)

@app.route('/')
def index():
    devices = commands.enumerate()
    return render_template('index.html', devices=str(devices))


