import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return jsonify({"message": "Hello World"}), 200


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host=host, port=port)

