#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug.serving import run_simple
from adsmutils import ADSFlask
from flask_restful import Api
from views import bp
import requests
import json

def create_app(**config):
    """
    Create the application and return it to the user
    :return: flask.Flask application
    """

    app = SimulateurADSFlask('simulateur', **config)
    app.url_map.strict_slashes = False    
    app.register_blueprint(bp)
    return app


class SimulateurADSFlask(ADSFlask):
    
    def search(self, **params):
        url = '%s/search/query' % self.config.get("API_ENDPOINT")
        assert 'q' in params
        # always get those fields
        if 'fl' not in params or not params['fl']:
            params['fl'] = 'bibcode,score,title'
        else:
            params['fl'] += 'bibcode,score,title'
        # always set those
        params['debugQuery'] = 'true'
        params['wt'] = 'json'
        
        r = requests.get(url, params=params)
        r.raise_for_status()
        return json.loads(r.raw)