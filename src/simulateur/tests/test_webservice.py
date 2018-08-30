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
        
    
    def test_query(self):
        self.app.save_experiment(None)
        f = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/title:foo.json'))
        with mock.patch.object(self.app, '_search', return_value=open(f, 'r').read()) as _m:
            r = self.client.get('/query/1', 
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
    
    def test_experiment(self):
        r = self.client.get('/experiment/0')
        assert r.json['eid'] == 1
        
        r = self.client.post(url_for('simulateur.experiment', experimentid='0'),
                data=json.dumps({'verb': 'save-experiment',
                                 'data': {
                                     'kRange': [0.5, 0.9],
                                     'bRange': [0.0, 1.0],
                                     'qparams': {'q': 'title:foo',
                                                 'foo': 'bar'},
                                     'fieldBoost': 'classic-factor',
                                     'normalizeWeight': True
                                    }}),
                content_type='application/json')
        assert r.json['eid'] == 2
        assert r.json['experiment_params'] == {u'qparams': {u'q': u'title:foo', u'foo': u'bar'}, u'normalizeWeight': True, u'fieldBoost': u'classic-factor', u'kRange': [0.5, 0.9], u'bRange': [0.0, 1.0]}
        
        
        r = self.client.post(url_for('simulateur.experiment', experimentid='2'),
                data=json.dumps({'verb': 'update-experiment',
                                 'data': {
                                     'fieldBoost': 'none',
                                     'reporter': 'rchyla@cfa'
                                    }}),
                content_type='application/json')
        assert r.json['eid'] == 2
        assert r.json['experiment_params'] == {u'qparams': {u'q': u'title:foo', u'foo': u'bar'}, u'normalizeWeight': True, u'fieldBoost': u'none', u'kRange': [0.5, 0.9], u'bRange': [0.0, 1.0]}
        assert r.json['reporter'] == 'rchyla@cfa'
        
        
        r = self.client.post(url_for('simulateur.experiment', experimentid='2'),
                data=json.dumps({'verb': 'add-relevant',
                                 'data': [123, 6789]}),
                content_type='application/json')
        assert r.json['eid'] == 2
        assert r.json['relevant'] == [123, 6789]
        
        
        r = self.client.post(url_for('simulateur.experiment', experimentid='2'),
                data=json.dumps({'verb': 'remove-relevant',
                                 'data': [123, 000]}),
                content_type='application/json')
        assert r.json['eid'] == 2
        assert r.json['relevant'] == [6789]
        
        r = self.client.post(url_for('simulateur.experiment', experimentid='2'),
                data=json.dumps({'verb': 'replace-relevant',
                                 'data': [334, 000]}),
                content_type='application/json')
        assert r.json['eid'] == 2
        assert r.json['relevant'] == [334, 000]
        
        
if __name__ == '__main__':
  unittest.main()
