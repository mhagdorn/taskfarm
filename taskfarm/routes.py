from taskfarm import app, db
from flask_httpauth import HTTPBasicAuth
from flask import jsonify, request,abort,g
import json
from uuid import uuid4
from datetime import datetime
from .models import *


auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/api/run', methods=['POST'])
@auth.login_required
def create_run():
    # create a new run
    if not request.json or not 'numTasks' in request.json:
        abort(400)

    run = Run(uuid = uuid4().hex, numTasks = json.loads(request.json)['numTasks'])
    db.session.add(run)
    # create the tasks
    for i in range(run.numTasks):
        db.session.add(Task(task=i,run=run))
    db.session.commit()
    return jsonify(run.to_dict), 201

@app.route('/api/runs', methods=['GET'])
@auth.login_required
def get_all_runs():
    results = []
    for run in Run.query.all():
        results.append(run.to_dict)

    return jsonify(results),200

@app.route('/api/runs/<string:uuid>', methods=['GET','DELETE'])
@auth.login_required
def get_run(uuid):
    run = Run.query.filter_by(uuid=uuid).first()
    if not run:
        abort(404)

    if request.method == 'GET':
        info = request.args.get('info', '')
        if info == '':
            result = run.full_status
        elif info in ['percentDone','numWaiting','numDone','numComputing']:
            result = {info: getattr(run,info)}
        else:
            abort(404)
        return jsonify(result), 200
    elif request.method == 'DELETE':
        db.session.query(Task).filter_by(run_id = run.id).delete()
        db.session.delete(run)
        db.session.commit()
        return '',204
    abort(500)
        
@app.route('/api/runs/<string:uuid>/restart', methods=['POST'])
@auth.login_required
def restart_tasks(uuid):
    run = Run.query.filter_by(uuid=uuid).first()
    if not run:
        abort(404)
    restart_all = request.args.get('all', 'False')
    if restart_all == 'True':
        db.session.query(Task).filter_by(run_id = run.id).update({'status' :TaskState.waiting,'percentCompleted':0.})
    elif restart_all == 'False':
        db.session.query(Task).filter(Task.run_id == run.id,Task.percentCompleted<100).update({'status' :TaskState.waiting})
    else:
        abort(404)
    db.session.commit()
    return '', 204
        
@app.route('/api/runs/<string:uuid>/task', methods=['POST'])
@auth.login_required
def get_task(uuid):
    run = Run.query.filter_by(uuid=uuid).first()
    if not run:
        abort(404)
    if not request.json or not 'worker_uuid' in request.json:
        abort(400)
    worker_uuid = json.loads(request.json)['worker_uuid']

    worker = Worker.query.filter_by(uuid=worker_uuid).first()
    if not worker:
        abort(404)

    task = db.session.query(Task).with_for_update().filter_by(status = TaskState.waiting,run_id = run.id).first()
    if task is None:
        return '',204
    task.status = TaskState.computing
    task.started = datetime.now()
    task.worker = worker
    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict), 201
        
@app.route('/api/runs/<string:uuid>/tasks/<int:task>', methods=['GET','PUT'])
@auth.login_required
def taskInfo(uuid,task):
    run = Run.query.filter_by(uuid=uuid).first()
    if not run:
        abort(404)
    task = Task.query.filter_by(run_id = run.id,task=task).first()
    if not task:
        abort(404)

    if request.method == 'GET':
        info = request.args.get('info', '')
        if info == '':
            result = task.to_dict
        elif info in ['status','percentCompleted']:
            result = {info:task.to_dict[info]}
        else:
            abort(404)
        return jsonify(result), 200
    elif request.method == 'PUT':
        if not request.json:
            abort(400)
        data = json.loads(request.json)
        for info in data:
            try:
                setattr(task,info,data[info])
            except Exception as e:
                return str(e), 400
        task.updated = datetime.now()
        db.session.add(task)
        db.session.commit()    
        return '',204
    abort(500)
    
@app.route('/api/worker', methods=['POST'])
@auth.login_required
def create_worker():
    if not request.json:
        abort(400)
    data = json.loads(request.json)
    for k in ['uuid','hostname','pid']:
        if k not in data:
            abort(400)
    worker = Worker(uuid=data['uuid'],
                    hostname = data['hostname'],
                    pid = data['pid'],
                    start = datetime.now()
                    )
    db.session.add(worker)
    db.session.commit()

    return jsonify({'uuid':worker.uuid,'id':worker.id}), 201

