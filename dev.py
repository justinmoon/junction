from flask_cors import CORS

from frontend import app

# hack to run hot-reloading react app in development ...
CORS(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
