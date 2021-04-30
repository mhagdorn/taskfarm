from flask_testing import TestCase

from taskfarm import app, db
from taskfarm.models import User
import base64
from uuid import uuid1

user = 'test'
passwd = 'test'

headers = {}
headers['Authorization'] = 'Basic ' + base64.b64encode(
    (user + ':' + passwd).encode('utf-8')).decode('utf-8')


class TaskfarmTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

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
        self.assertFalse(u.verify_password(p + 'not'))

        db.session.add(u)
        db.session.commit()

        assert u in db.session

    def test_get_auth_token(self):
        response = self.app.get('/api/token', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_auth_with_token(self):
        response = self.app.get('/api/token', headers=headers)
        token = response.get_json()['token']

        h = {}
        h['Authorization'] = 'Basic ' + base64.b64encode(
            token.encode('utf-8') + b': ').decode('utf-8')
        h['Content-Type'] = 'application/json'
        h['Accept'] = 'application/json'

        response = self.app.get('/api/token', headers=h)
        self.assertEqual(response.status_code, 200)

    def create_run(self, numTasks):
        response = self.app.post('/api/run',
                                 headers=headers,
                                 json={'numTasks': numTasks})
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def create_worker(self, hostname, pid):
        data = {'uuid': uuid1().hex,
                'hostname': hostname,
                'pid': pid}
        response = self.app.post('/api/worker',
                                 headers=headers,
                                 json=data)
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def get_run_info(self, run_uuid, info=None, status=200):
        data = {}
        if info is not None:
            data['info'] = info
        response = self.app.get('/api/runs/' + run_uuid,
                                headers=headers, query_string=data)
        self.assertEqual(response.status_code, status)
        return response.get_json()

    def restart_run(self, run_uuid, all=None, status=204):
        data = {}
        if all is not None:
            data['all'] = all
        response = self.app.post('/api/runs/{}/restart'.format(run_uuid),
                                 headers=headers, query_string=data)
        self.assertEqual(response.status_code, status)

    def get_task(self, run_uuid, worker_uuid, status=201):
        response = self.app.post('/api/runs/{}/task'.format(run_uuid),
                                 headers=headers,
                                 json={'worker_uuid': worker_uuid})
        self.assertEqual(response.status_code, status)
        return response.get_json()

    def get_task_info(self, run, task, info='', status=200):
        args = {}
        if len(info) > 0:
            args['info'] = info
        response = self.app.get('/api/runs/{}/tasks/{}'.format(run, task),
                                headers=headers,
                                query_string=args)
        self.assertEqual(response.status_code, status)
        return response.get_json()

    def update_task_info(self, run, task, info, status=204):
        response = self.app.put('/api/runs/{}/tasks/{}'.format(run, task),
                                headers=headers,
                                json=info)
        self.assertEqual(response.status_code, status)

    def test_create_run(self):
        nt = 10
        run = self.create_run(nt)
        self.assertEqual(run['numTasks'], nt)

    def test_get_all_runs(self):
        numTasks = [10, 20, 30]
        runs = []
        for nt in numTasks:
            run = self.create_run(nt)
            runs.append(run)
        response = self.app.get('/api/runs', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()['data']
        for i in range(len(runs)):
            self.assertDictEqual(runs[i], data[i])

    def test_get_run(self):
        nt = 10
        run = self.create_run(nt)

        response = self.app.get('/api/runs/' + run['uuid'], headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['uuid'], run['uuid'])
        self.assertEqual(data['numTasks'], nt)
        for k in ['numComputing', 'numDone', 'numWaiting', 'percentDone']:
            self.assertEqual(data[k], 0)

    def test_get_run_na(self):
        response = self.app.get('/api/runs/no_such_run', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_get_run_info_all(self):
        nt = 10
        run = self.create_run(nt)
        rinfo = self.get_run_info(run['uuid'])
        for k in run:
            self.assertEqual(run[k], rinfo[k])

    def test_get_run_info(self):
        nt = 10
        run = self.create_run(nt)
        for i in ['percentDone', 'numWaiting', 'numDone', 'numComputing']:
            self.get_run_info(run['uuid'], info=i)
        self.get_run_info(run['uuid'], info='blub', status=404)

    def test_delete_run(self):
        run = self.create_run(10)
        response = self.app.delete('/api/runs/' + run['uuid'], headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_delete_run_na(self):
        response = self.app.delete('/api/runs/no_such_run', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_create_worker(self):
        self.create_worker('blub', 1000)

    def test_get_task_noworker(self):
        nt = 10
        run = self.create_run(nt)
        response = self.app.post('/api/{}/task'.format(run['uuid']),
                                 headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_get_task_wrongworker(self):
        nt = 10
        run = self.create_run(nt)
        self.get_task(run['uuid'], 'no_worker', status=404)

    def test_get_task_norun(self):
        worker = self.create_worker('blub', 1000)
        self.get_task('norun', worker['uuid'], status=404)

    def test_get_task(self):
        nt = 10
        run = self.create_run(nt)
        worker = self.create_worker('blub', 1000)
        # create all tasks
        for i in range(nt):
            task = self.get_task(run['uuid'], worker['uuid'])
            self.assertEqual(task['percentCompleted'], 0)
            self.assertEqual(task['status'], 'computing')
            self.assertEqual(task['task'], i)
        # and another one which should indicate all tasks are handed out
        task = self.get_task(run['uuid'], worker['uuid'], status=204)

        # all tasks should have status computing and
        # there should be no waiting tasks
        rinfo = self.get_run_info(run['uuid'])
        self.assertEqual(rinfo['numComputing'], nt)
        self.assertEqual(rinfo['numWaiting'], 0)

    def test_get_task_info_norun(self):
        self.get_task_info('norun', 1, status=404)

    def test_get_task_info_outofrange(self):
        nt = 10
        run = self.create_run(nt)
        self.get_task_info(run['uuid'], -1, status=404)
        self.get_task_info(run['uuid'], nt, status=404)

    def test_get_task_info_wronginfo(self):
        nt = 10
        run = self.create_run(nt)
        self.get_task_info(run['uuid'], 0,
                           info='no_such_thing', status=404)

    def test_get_existing_task_info(self):
        nt = 10
        run = self.create_run(nt)
        worker = self.create_worker('blub', 1000)
        task = self.get_task(run['uuid'], worker['uuid'])

        tinfo = self.get_task_info(run['uuid'], task['task'])
        self.assertDictEqual(task, tinfo)

    def test_get_task_info(self):
        nt = 10
        run = self.create_run(nt)
        # create new tasks on the fly
        tid = 0
        tinfo = self.get_task_info(run['uuid'], tid, status=200)
        self.assertEqual(tinfo['task'], tid)

        for i in ['status', 'percentCompleted']:
            ti = self.get_task_info(run['uuid'], tid, info=i, status=200)
            self.assertEqual(tinfo[i], ti[i])

    def test_update_task_info_nothing(self):
        nt = 10
        run = self.create_run(nt)
        self.update_task_info(run['uuid'], 0, None, status=400)

    def test_update_task_info(self):
        nt = 10
        run = self.create_run(nt)
        tid = 0

        for pc in [10, 20, 50.5, 100]:
            self.update_task_info(run['uuid'], tid, {'percentCompleted': pc})

        for s in ['waiting', 'computing', 'done']:
            self.update_task_info(run['uuid'], tid, {'status': s})

    def test_update_task_info_wrong(self):
        nt = 10
        run = self.create_run(nt)
        tid = 0

        self.update_task_info(run['uuid'], tid,
                              {'stat': 'wrong'}, status=400)
        self.update_task_info(run['uuid'], tid,
                              {'status': 'wrong'}, status=400)

    def test_get_task_waiting(self):
        nt = 10
        run = self.create_run(nt)
        worker = self.create_worker('blub', 1000)
        # create all tasks
        for i in range(nt):
            task = self.get_task(run['uuid'], worker['uuid'])

        # reset a particular task
        tid = 5
        self.update_task_info(run['uuid'], tid, {'status': 'waiting'})
        rinfo = self.get_run_info(run['uuid'])
        self.assertEqual(rinfo['numComputing'], nt - 1)

        task = self.get_task(run['uuid'], worker['uuid'])
        self.assertEqual(task['task'], tid)

    def test_restart_run_norun(self):
        self.restart_run('no_run', status=404)

    def test_restart_run_wrongparam(self):
        nt = 10
        run = self.create_run(nt)
        self.restart_run(run['uuid'], all='wrong', status=404)

    def test_restart_run(self):
        nt = 10
        run = self.create_run(nt)
        for i in range(0, nt, 2):
            self.update_task_info(run['uuid'], i,
                                  {'status': 'done',
                                   'percentCompleted': 100})
        for i in range(1, nt, 2):
            self.update_task_info(run['uuid'], i,
                                  {'status': 'computing',
                                   'percentCompleted': 50})
        rinfo = self.get_run_info(run['uuid'])
        self.assertEqual(rinfo['numWaiting'], 0)
        self.assertEqual(rinfo['numComputing'], nt / 2)
        self.assertEqual(rinfo['numDone'], nt / 2)

        self.restart_run(run['uuid'])
        rinfo = self.get_run_info(run['uuid'])
        self.assertEqual(rinfo['numWaiting'], nt / 2)
        self.assertEqual(rinfo['numComputing'], 0)
        self.assertEqual(rinfo['numDone'], nt / 2)

    def test_restart_run_all(self):
        nt = 10
        run = self.create_run(nt)
        for i in range(0, nt, 2):
            self.update_task_info(run['uuid'], i,
                                  {'status': 'done',
                                   'percentCompleted': 100})
        for i in range(1, nt, 2):
            self.update_task_info(run['uuid'], i,
                                  {'status': 'computing',
                                   'percentCompleted': 50})
        rinfo = self.get_run_info(run['uuid'])
        self.assertEqual(rinfo['numWaiting'], 0)
        self.assertEqual(rinfo['numComputing'], nt / 2)
        self.assertEqual(rinfo['numDone'], nt / 2)

        self.restart_run(run['uuid'], all='True')
        rinfo = self.get_run_info(run['uuid'])
        self.assertEqual(rinfo['numWaiting'], nt)
        self.assertEqual(rinfo['numComputing'], 0)
        self.assertEqual(rinfo['numDone'], 0)
