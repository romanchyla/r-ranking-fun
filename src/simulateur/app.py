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
from rfun.evaluation import MultiParameterEvaluator
from collections import OrderedDict
from simulateur.models import Experiment
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
        self.parser = ExplanationParser(use_kwargs=True, flatten_tfidf=True)
    
    def query(self, **params):
        
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
        return self._query(**params)
        
    
    def _query(self, **params):
        url = '%s/search/query' % self.config.get("API_ENDPOINT")
        r = requests.get(url, params=params,
                     headers = {'Authorization': 'Bearer {0}'.format(self.config.get('API_TOKEN'))})
        r.raise_for_status()
        #print r.text
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
    
    def get_experiment(self, experimentid):
        with self.session_scope() as session:
            m = session.query(Experiment).filter(Experiment.eid == int(experimentid)).first()
            if not m:
                return None
            return m.toJSON()
    
    def save_experiment(self, experimentid,
                        reporter=None,
                        query_results=None, 
                        experiment_params=None,
                        relevant=None,
                        query=None,
                        description=None,
                        experiment_results=None):
        with self.session_scope() as session:
            if experimentid is None:
                m = Experiment()
                session.add(m)
            else:
                m = session.query(Experiment).filter_by(eid=experimentid).first()
                if not m:
                    m = Experiment()
                    session.add(m)
            if description:
                m.description = description
            if query:
                m.query = query
            if reporter:
                m.reporter = reporter
    
            if experiment_params:
                m.experiment_params = json.dumps(experiment_params)
            
                
            if query_results:
                m.query = query_results['responseHeader']['params']['q']
                m.query_results = json.dumps(query_results)
            
            if experiment_results:
                m.experiment_results = json.dumps(experiment_results)
            
            if relevant:
                m.relevant = json.dumps(relevant)
                
            if session.dirty:
                m.updated = get_date()
            session.commit()
            return m.toJSON()


    def run_experiment(self, experimentid, num_results=5):
        """Will execute the experiment."""
        exp = self.get_experiment(experimentid)
        if exp is None:
            raise Exception('Experiment %s doesnt exist' % experimentid)
        
        # check we have all necessary data
        assert len(exp['relevant']) > 0
        assert len(exp['query_results']['response']['docs']) > 0
        assert 'formula' in exp['query_results']['response']['docs'][0]
        assert len(exp['experiment_params'].keys()) > 0
        
        gold_set = exp['relevant']
        docs = exp['query_results']['response']['docs']
        params = exp['experiment_params']
        
        se = MultiParameterEvaluator(
            [25, 50, 100], # TODO: make ocnfigurable
            docs, 
            gold_set, 
            params.get('kRange', [1.2, 1.2, 0.1]), 
            params.get('bRange', [0.75, 0.75, 0.1]),
            params.get('docLenRange', None), 
            normalizeWeight='useNormalization' in params,
            fieldBoost=params.get('fieldBoost', None))
        
        size = se.get_size()
        
        with self.session_scope() as session:
            
            m = session.query(Experiment).filter(Experiment.eid == int(experimentid)).first()
            m.progress = 0.0
            m.started = get_date()
            m.finished = None
            session.commit()
            
            for tick, best_sofar in se.run():
                m = session.query(Experiment).filter(Experiment.eid == int(experimentid)).first()
                m.progress = size / tick
                session.commit()
        
            m = session.query(Experiment).filter(Experiment.eid == int(experimentid)).first()
            m.progress = 1.0
            m.finished = get_date()
            m.experiment_results = json.dumps({'runs': size, 'params': params, 'results': se.get_results(),
                                               'elapsed': m.finished - m.started})
            session.commit()
                
        return 
        
            
            
            
            