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
from werkzeug.exceptions import HTTPException, default_exceptions
from flask import jsonify
import traceback
from rfun.scoring import FlexibleScorer


def create_app(**config):
    """
    Create the application and return it to the user
    :return: flask.Flask application
    """

    app = SimulateurADSFlask('simulateur', local_config=config)
    app.url_map.strict_slashes = False    
    app.register_blueprint(bp)
    
    # Register custom error handlers
    if not app.config.get('DEBUG'):
        def error_handler(error):
            code = 500
            if isinstance(error, HTTPException):
                code = error.code
            return jsonify(code=code, error=str(error), stacktrace=traceback.format_exc())
        
        for exc in default_exceptions:
            app.register_error_handler(exc, error_handler)
        app.register_error_handler(Exception, error_handler)
        
    return app


class SimulateurADSFlask(ADSFlask):
    
    def __init__(self, *args, **kwargs):
        ADSFlask.__init__(self, *args, **kwargs)
        self.parser = ExplanationParser(use_kwargs=True, flatten_tfidf=True)
        self.scorers = {
            'standard': {'name': 'standard',
                         'impl': FlexibleScorer,
                         'descr': 'Standard scorer executing grid search over all parameters'},
            'boost': {'name': 'standard search + boost',
                      'impl': FlexibleScorerWithBoost,
                      'descr': 'Grid search with additional boosting of the final score using <score> * (1 + <boost_factor)',
                      'evaluator': FunnyMultiParameterEvaluator}
        }
    
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
                m.started = None
                m.finished = None
                m.progress = 0.0
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
        doclen = boost = const = None
        
        if params.get('useBoost', False):
            boost = params.get('boostSelection', None)
            
        if params.get('useDocLen', False):
            doclen = params.get('docLenRange', None)
            
        if params.get('useConstant', False):
            const = {'fields': params.get('constSelection', []),
                     'range': params.get('constRange', [0, 0, 0])}
            
        evaluator_impl, scorer_impl = self.get_runners(params)
        
        se = evaluator_impl(
            [25, 50, 100], # TODO: make ocnfigurable
            docs, 
            gold_set, 
            kRange = params.get('useK', False) and params.get('kRange', [0.01, 1.2, 0.1]) or None, 
            bRange=params.get('useB', False) and params.get('bRange', [0.01, 1.2, 0.1]) or None,
            docLenRange=doclen, 
            normalizeWeight=params.get('useNormalization', False),
            fieldBoost=boost,
            constRanges=const,
            scorer_impl=scorer_impl
            )
        
        size = float(se.get_size())
        
        with self.session_scope() as session:
            
            m = session.query(Experiment).filter(Experiment.eid == int(experimentid)).first()
            m.progress = 0.0
            m.started = get_date()
            m.finished = None
            session.commit()
            
            for tick, best_sofar in se.run(yield_per=int(size/20)):
                self.logger.info('Expriment %s progress: %s/%s (%s), best so far: %s', 
                                 experimentid, tick, size, tick/size, best_sofar)
                m = session.query(Experiment).filter(Experiment.eid == int(experimentid)).first()
                m.progress = tick / size
                session.commit()
        
            m = session.query(Experiment).filter(Experiment.eid == int(experimentid)).first()
            m.progress = 1.0
            m.finished = get_date()
            m.experiment_results = json.dumps({'runs': size, 'params': params, 'results': se.get_results(),
                                               'elapsed': (m.finished - m.started).total_seconds()})
            session.commit()
                
        return


    def get_runners(self, params):
        evaluator_impl = MultiParameterEvaluator
        if params.get('scorerSelection', None):
            sname = params.get('scorerSelection')
            if sname not in self.scorers:
                raise Exception('Unkwnown scorer %s', sname)
            scorer_impl = self.scorers[sname]['impl']
            evaluator_impl = self.scorers[sname].get('evaluator', MultiParameterEvaluator)
        else:
            scorer_impl = FlexibleScorer
        return evaluator_impl, scorer_impl


class FunnyMultiParameterEvaluator(MultiParameterEvaluator):
    def score(self, scorer, kwargs):
        max_score = 0.0
        for ac in self._xrange(0.0, 2.0, 0.25):
            score = self._score(scorer, ac=ac)
            if score > max_score:
                max_score = score
                kwargs['ac'] = ac
        return score

class FlexibleScorerWithBoost(FlexibleScorer):
    """Instead of boosting every query clause,
    the boost is only applied at the end.
    
    Additionally, we also simulate something i
    am calling alberto_constant
    
    """
    
    def run(self, formula, **kwargs):
        if self.idf_normalization:
            self.idf_normalization_factor = self.normalizer.run(formula)
        else:
            self.idf_normalization_factor = None
        
        docboost = self.get_boost(None, kwargs.get('docid', None), 1.0)
        score = self._eval(formula, **kwargs)
        albertos_constant = kwargs.get('ac', self.extra.get('ac', 0.0))
        return score * (albertos_constant + docboost)


    def const(self, query, boost, querynorm):
        return querynorm * boost
            