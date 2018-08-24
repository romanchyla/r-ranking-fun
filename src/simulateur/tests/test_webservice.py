from flask.ext.testing import TestCase
from flask import url_for, request
import unittest
from simulateur.models import Base, Experiment
import json
import os
from mock import mock

class TestServices(TestCase):
    '''Tests that each route is an http response'''

    def create_app(self):
        '''Start the wsgi application'''
        from simulateur import app
        a = app.create_app(**{
               'SQLALCHEMY_DATABASE_URI': 'sqlite://',
               'SQLALCHEMY_ECHO': False,
               'TESTING': True,
               'PROPAGATE_EXCEPTIONS': True,
               'TRAP_BAD_REQUEST_ERRORS': True
            })
        Base.metadata.bind = a.db.session.get_bind()
        Base.metadata.create_all()
        return a


    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Base.metadata.drop_all()
        self.app.db = None


    def test_dashboard(self):
        # create some experiments
        for i in range(99):
            self.app.save_experiment(None)
        
        r = self.client.get('/dashboard')
        self.assertEqual(r.status_code,200)
        d = json.loads(r.data)
    
        assert d['header']['remaining'] == 49
        assert len(d['results']) == 50
        assert d['results'][0]['eid'] == 1
        assert d['results'][-1]['eid'] == 50
        
        
        r = self.client.get('/dashboard/98/20')
        self.assertEqual(r.status_code,200)
        d = json.loads(r.data)

        assert d['header']['remaining'] == 0
        assert len(d['results']) == 2
        assert d['results'][0]['eid'] == 98
        assert d['results'][-1]['eid'] == 99
        
    
    def test_search(self):
        self.app.save_experiment(None)
        f = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/title:foo.json'))
        with mock.patch.object(self.app, '_search', return_value=open(f, 'r').read()) as _m:
            r = self.client.get('/search/1', 
                            query_string={'fl': 'title,abstract,foo', 'q': 'title:foo'},
                            content_type='application/json')
            assert 'formula' in r.data
            with self.app.session_scope() as session:
                m = session.query(Experiment).filter_by(eid=1).first()
                j = m.toJSON()
                assert j['created']
                assert j['updated']
                assert j['created'] != j['updated']
                assert len(j['query_results']['response']['docs']) > 0
                assert len(filter(lambda x: 'formula' in x, j['query_results']['response']['docs'])) > 0
                
        
if __name__ == '__main__':
  unittest.main()
