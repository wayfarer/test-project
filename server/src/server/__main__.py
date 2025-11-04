import os
from server import app

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host=host, port=port)

