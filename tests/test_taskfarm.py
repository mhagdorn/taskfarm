#import unittest
from flask import Flask
from flask_testing import TestCase

from taskfarm import app,db
from taskfarm.models import User
from requests.auth import HTTPBasicAuth
import base64
import json

user = 'test'
passwd = 'test'

headers = {}
headers['Authorization'] = 'Basic ' + base64.b64encode((user + ':' + passwd).encode('utf-8')).decode('utf-8')


class TaskfarmTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        # pass in test configuration
        return app
    
    def setUp(self):
        self.app = app.test_client()
        
        db.create_all()
        # create user
        u = User(username=user)
        u.hash_password(passwd)
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user(self):
        u = 'test2'
        p = 'testing'
        u = User(username=u)
        u.hash_password(p)
        self.assertTrue(u.verify_password(p))
        self.assertFalse(u.verify_password(p+'not'))

        db.session.add(u)
        db.session.commit()

        assert u in db.session
        
    def test_get_auth_token(self):
        response = self.app.get('/api/token', headers=headers)
        self.assertEqual(response.status_code, 200)
 
    def test_auth_with_token(self):
        response = self.app.get('/api/token', headers=headers)
        token = json.loads(response.data)['token']

        h = {}
        h['Authorization'] = 'Basic ' + base64.b64encode(token.encode('utf-8')+b':').decode('utf-8')
        h['Content-Type'] = 'application/json'
        h['Accept'] = 'application/json'
        
        response = self.app.get('/api/token', headers=h)
        self.assertEqual(response.status_code, 200)

    def create_run(self,numTasks):
        response = self.app.post('/api/run',
                                 headers=headers,
                                 json={'numTasks':numTasks})
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_create_run(self):
        nt=10
        run = self.create_run(nt)
        self.assertEqual(run['numTasks'],nt)

    def test_get_all_runs(self):
        numTasks = [10,20,30]
        runs = []
        for nt in numTasks:
            run = self.create_run(nt)
            runs.append(run)
        response = self.app.get('/api/runs',
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()['data']
        for i in range(len(runs)):
            self.assertDictEqual(runs[i],data[i])
            
    def test_get_run(self):
        nt=10
        run = self.create_run(nt)

        response = self.app.get('/api/runs/'+run['uuid'], headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['uuid'],run['uuid'])
        self.assertEqual(data['numTasks'],nt)
        for  k in ['numComputing','numDone','numWaiting','percentDone']:
            self.assertEqual(data[k],0)

    def test_get_run_na(self):
        response = self.app.get('/api/runs/no_such_run', headers=headers)
        self.assertEqual(response.status_code, 404)
            
    def test_delete_run(self):
        run = self.create_run(10)

        response = self.app.delete('/api/runs/'+run['uuid'], headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_delete_run_na(self):
        response = self.app.delete('/api/runs/no_such_run', headers=headers)
        self.assertEqual(response.status_code, 404)
