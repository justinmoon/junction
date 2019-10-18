import os
from flask import Flask, send_from_directory, render_template
from api import api, schema
from flask_cors import CORS
from disk import ensure_datadir

server = Flask(__name__, static_folder="build/static", template_folder="build")
CORS(server)

server.register_blueprint(api)
schema.init_app(server)

@server.route("/")
def index():
    return render_template('index.html')

def serve_windows():
    from waitress import serve
    serve(server, host='0.0.0.0', port=37128)

def serve_unix():
    # TODO: uwsgi
    # server.run(host='0.0.0.0', port=37128, threaded=False)
    server.run(host='0.0.0.0', port=37128, threaded=True)

if __name__ == '__main__':
    # Run dev server
    server.run(debug=True, host='0.0.0.0', port=37128, threaded=False)        
