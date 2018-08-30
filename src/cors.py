
from flask_cors import CORS
from simulateur.app import create_app

application = create_app() 
cors = CORS(application,  resources=r'/*', headers='*', expose_headers=['Content-Type', 'Accept', 'Credentials', 'Authorization', 'content-type'])

if __name__ == '__main__':
    application.run('0.0.0.0', port=4000, debug=False)
