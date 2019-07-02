from flask import Flask
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    r = subprocess.run(["bitcoin-cli", "listtransactions"], capture_output=True)
    return (r.stdout.decode('utf-8'))
    # return "Hello World!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)