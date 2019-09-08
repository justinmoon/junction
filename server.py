from flask import Flask
from api import api, schema

server = Flask(__name__)

server.register_blueprint(api)
schema.init_app(server)

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)
