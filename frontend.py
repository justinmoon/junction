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
