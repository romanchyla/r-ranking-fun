
import unittest
from simulateur.app import SimulateurADSFlask
import os, json
from mock import mock
from simulateur.models import Base

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
        with mock.patch.object(app, '_search', return_value='something') as _m:
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



if __name__ == '__main__':
    unittest.main()