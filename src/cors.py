
from flask_cors import CORS
from simulateur.app import create_app

if __name__ == '__main__':
    app = create_app()
    cors = CORS(app,  resources=r'/*', headers='*', expose_headers=['Content-Type', 'Accept', 'Credentials', 'Authorization', 'content-type'])
    app.run('0.0.0.0', port=4000, debug=False)
