
import unittest
from simulateur.app import SimulateurADSFlask
import os, json
from mock import mock
from simulateur.models import Base
import simulateur

class TestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.app = SimulateurADSFlask('test', local_config=\
            {
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
            'SQLALCHEMY_ECHO': False
            })
        Base.metadata.bind = self.app.db.session.get_bind()
        Base.metadata.create_all()
    
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Base.metadata.drop_all()
        self.app.db = None

    def test_enhance(self):
        app = self.app
        f = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/example-debug-query.json'))
        r = app.enhance_solr_results(open(f, 'r').read())
        #print json.dumps(r, indent=True)
        assert len(filter(lambda x: 'formula' in x, r['response']['docs'])) == 10
        assert len(filter(lambda x: 'docid' in x, r['response']['docs'])) == 10
        assert len(filter(lambda x: 'score' in x, r['response']['docs'])) == 10
        
        assert 'sum(sum(sum' in r['response']['docs'][0]['formula']
         
    
    def test_search(self):
        app = self.app
        with mock.patch.object(app, '_query', return_value='something') as _m:
            r = app.query(q='foo', fl='whatever')
            _m.assert_called_with(debugQuery='true', fl='whatever,bibcode,score,title', q='foo', rows=100, sort='score desc', wt='json')


    def test_save(self):
        app = self.app
        r = app.save_experiment(None, query_results={'responseHeader': {'params': {'q': 'foo:bar'}}, 'foo': 'bar'})
        assert r['eid'] == 1
        assert r['updated'] is None
        assert r['created']
        assert r['query_results'] != {}
        assert r['experiment_params'] == {}
        assert r['query'] == 'foo:bar'
        
        
        r = app.save_experiment(1, query_results={'responseHeader': {'params': {'q': 'baz'}}, 'foo': 'bar'})
        assert r['query'] == 'baz'
        assert r['updated']

    
    def test_runexperiment(self):
        app = self.app
        rv = {
            'relevant': range(10),
            'query_results' :{'responseHeader': {'params': {'q': 'baz'}}, 'foo': 'bar',
                              'response': {'docs': [{'docid': 1, 'formula': 'sum(1, 1)'}]}},
            'experiment_params': {'scorerSelection': 'boost'}
            
        }
        app.save_experiment(None)
        with mock.patch.object(app, 'get_experiment', return_value=rv):
            app.run_experiment('1')
            
        exp = self.app.get_experiment('1')
        r = exp['experiment_results']['results']
        assert len(r) > 0
        e,s = app.get_runners(rv['experiment_params'])
        scorer = s(**r[0][1])
        assert isinstance(scorer, simulateur.app.FlexibleScorerWithBoost)
        assert 'ac' in scorer.extra
        
        assert scorer.run('sum(1, 1)') == 2
        scorer.extra['ac'] = 5.0
        assert scorer.run('sum(1, 1)') == 12

if __name__ == '__main__':
    unittest.main()