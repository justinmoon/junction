from flask import Flask
from api import api, schema
from flask_cors import CORS
from disk import ensure_datadir

server = Flask(__name__)
CORS(server)

server.register_blueprint(api)
schema.init_app(server)

if __name__ == '__main__':
    ensure_datadir()
    server.run(debug=True, host='0.0.0.0', port=37128, threaded=False)
