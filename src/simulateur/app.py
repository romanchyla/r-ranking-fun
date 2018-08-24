#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug.serving import run_simple
from adsmutils import ADSFlask
from flask_restful import Api
from views import bp
import requests
import json
import copy
from rfun.scoring import ExplanationParser
from collections import OrderedDict
from simulateur import models
from adsmutils import get_date

def create_app(**config):
    """
    Create the application and return it to the user
    :return: flask.Flask application
    """

    app = SimulateurADSFlask('simulateur', local_config=config)
    app.url_map.strict_slashes = False    
    app.register_blueprint(bp)
    return app


class SimulateurADSFlask(ADSFlask):
    
    def __init__(self, *args, **kwargs):
        ADSFlask.__init__(self, *args, **kwargs)
        self.parser = ExplanationParser()
    
    def search(self, **params):
        
        assert 'q' in params
        if 'fl' in params and not isinstance(params['fl'], basestring):
            params['fl'] = ','.join(params['fl'])
            
        # always get those fields
        if 'fl' not in params or not params['fl']:
            params['fl'] = 'bibcode,score,title'
        else:
            params['fl'] += ',bibcode,score,title'
        # always set those
        params['debugQuery'] = 'true'
        params['wt'] = 'json'
        # override if not set
        if 'rows' not in params:
            params['rows'] = self.config.get('MAX_ROWS', 100)
        if 'sort' not in params:
            params['sort'] = 'score desc'
        return self._search(**params)
        
    
    def _search(self, **params):
        url = '%s/search/query' % self.config.get("API_ENDPOINT")
        r = requests.get(url, params=params,
                     headers = {'Authorization': 'Bearer {0}'.format(self.config.get('API_TOKEN'))})
        r.raise_for_status()
        print r.text
        return r.text
    
    
    def enhance_solr_results(self, text):
        """Adds formula expressions into the search results."""
        
        if isinstance(text, basestring):
            j = json.loads(text, object_pairs_hook=OrderedDict)
        else:
            raise Exception('We insist on receiving the textual represenation (in order to properly track order), instead got: %s' % type(text))
            
        if 'debug' not in j and 'parsedquery' not in j['debug']:
            raise Exception('No debug output present in the solr response')
        
        query = j['debug']['querystring']
        parsed_query = j['debug']['parsedquery_toString']
        
        explanation = j['debug']['explain']
        
        parser = self.parser
        docs = j['response']['docs']
        
        i = 0
        for k,v in explanation.items():
            try:
                score, formula = parser.parse(v)
                if score > docs[i]['score']:
                    assert score - docs[i]['score'] < 0.00005
                else:
                    assert docs[i]['score'] - score < 0.00005
                docs[i]['docid'] = k
                docs[i]['score'] = score
                docs[i]['formula'] = formula
                i+=1
            except Exception, e:
                self.logger.error('Failed parsing: %s', v)
                raise e
        return j
    
    
    
    def save_experiment(self, experimentid,
                        reporter=None,
                        query_results=None, 
                        experiment_params=None,
                        experiment_results=None):
        with self.session_scope() as session:
            if experimentid is None:
                m = models.Experiment()
                session.add(m)
            else:
                m = session.query(models.Experiment).filter_by(eid=experimentid).first()
                if not m:
                    m = models.Experiment()
                    session.add(m)
            if reporter:
                m.reporter = reporter
    
            if experiment_params:
                m.experiment_params = json.dumps(experiment_params)
            
            if query_results:
                m.query = query_results['responseHeader']['params']['q']
                m.query_results = json.dumps(query_results)
            if experiment_results:
                m.experiment_results = json.dumps(experiment_results)
                
            if session.dirty:
                m.updated = get_date()
            session.commit()
            return m.toJSON()
            
            
            
            