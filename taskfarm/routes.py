from .application import app, db
from flask_httpauth import HTTPBasicAuth
from flask import jsonify, request, abort, g
from uuid import uuid4
from datetime import datetime
from .models import Worker, Task, Run, TaskState, User
import logging

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
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
    if not request.get_json() or 'numTasks' not in request.get_json():
        abort(400)

    run = Run(uuid=uuid4().hex, numTasks=request.get_json()['numTasks'])
    db.session.add(run)
    db.session.commit()
    return jsonify(run.to_dict), 201


@app.route('/api/runs', methods=['GET'])
@auth.login_required
def get_all_runs():
    results = []
    for run in Run.query.all():
        results.append(run.to_dict)
    return jsonify({'data': results}), 200


@app.route('/api/runs/<string:uuid>', methods=['GET', 'DELETE'])
@auth.login_required
def get_run(uuid):
    run = Run.query.filter_by(uuid=uuid).first()
    if not run:
        logging.error('no run with uuid={}'.format(uuid))
        abort(404)

    if request.method == 'GET':
        info = request.args.get('info', '')
        if info == '':
            result = run.full_status
        elif info in ['percentDone', 'numWaiting',
                      'numDone', 'numComputing']:
            result = {info: getattr(run, info)}
        else:
            abort(404)
        return jsonify(result), 200
    elif request.method == 'DELETE':
        db.session.query(Task).filter_by(run_id=run.id).delete()
        db.session.delete(run)
        db.session.commit()
        return '', 204
    abort(500)


@app.route('/api/runs/<string:uuid>/restart', methods=['POST'])
@auth.login_required
def restart_tasks(uuid):
    run = Run.query.filter_by(uuid=uuid).first()
    if not run:
        logging.error('no run with uuid={}'.format(uuid))
        abort(404)
    restart_all = request.args.get('all', 'False')
    if restart_all == 'True':
        db.session.query(Task).filter_by(run_id=run.id) \
                              .update({'status': TaskState.waiting,
                                       'percentCompleted': 0.})
    elif restart_all == 'False':
        db.session.query(Task).filter(Task.run_id == run.id,
                                      Task.percentCompleted < 100) \
                              .update({'status': TaskState.waiting})
    else:
        abort(404)
    db.session.commit()
    return '', 204


@app.route('/api/runs/<string:uuid>/task', methods=['POST'])
@auth.login_required
def get_task(uuid):
    if not request.get_json() or 'worker_uuid' not in request.get_json():
        abort(400)
    worker_uuid = request.get_json()['worker_uuid']

    worker = Worker.query.filter_by(uuid=worker_uuid).first()
    if not worker:
        logging.error('no worker with uuid={}'.format(worker_uuid))
        abort(404)

    run = db.session.query(Run).with_for_update().filter_by(uuid=uuid).first()
    if not run:
        logging.error('no run with uuid={}'.format(uuid))
        db.session.rollback()
        abort(404)

    task = db.session.query(Task).with_for_update() \
                                 .filter_by(status=TaskState.waiting,
                                            run_id=run.id).first()
    if not task and run.nextTask < run.numTasks:
        # no waiting tasks, create the next one
        if run.numListedTasks == run.nextTask:
            task = Task(task=run.nextTask, run=run)
            run.nextTask += 1
        else:
            for tid in range(run.nextTask, run.numTasks):
                t = Task.query.filter_by(run_id=run.id, task=tid).first()
                if not t:
                    task = Task(task=run.nextTask, run=run)
                    break
            run.nextTask = t+1
        db.session.add(run)

    if task:
        task.status = TaskState.computing
        task.started = datetime.now()
        task.worker = worker
        db.session.add(task)
    db.session.commit()

    if task is None:
        return '', 204
    else:
        return jsonify(task.to_dict), 201


@app.route('/api/runs/<string:uuid>/tasks/<int:taskID>',
           methods=['GET', 'PUT'])
@auth.login_required
def taskInfo(uuid, taskID):
    run = Run.query.filter_by(uuid=uuid).first()
    if not run:
        logging.error('no run with uuid={}'.format(uuid))
        abort(404)
    task = Task.query.filter_by(run_id=run.id, task=taskID).first()
    if not task:
        if taskID < 0 or taskID >= run.numTasks:
            logging.error('no taskID {} outside range(0,{})'
                          .format(taskID, run.numTasks))
            abort(404)

        # create a new task
        task = Task(task=taskID, run=run)
        db.session.add(task)
        if run.nextTask == taskID:
            run.nextTask += 1
            db.session.add(run)
        db.session.commit()

    if request.method == 'GET':
        info = request.args.get('info', '')
        if info == '':
            result = task.to_dict
        elif info in ['status', 'percentCompleted']:
            result = {info: task.to_dict[info]}
        else:
            abort(404)
        return jsonify(result), 200
    elif request.method == 'PUT':
        if not request.get_json():
            abort(400)
        data = request.get_json()
        for info in data:
            try:
                setattr(task, info, data[info])
            except Exception as e:
                return str(e), 400
        task.updated = datetime.now()
        db.session.add(task)
        try:
            db.session.commit()
        except Exception as e:
            return str(e), 400
        return '', 204
    abort(500)


@app.route('/api/worker', methods=['POST'])
@auth.login_required
def create_worker():
    if not request.get_json():
        abort(400)
    data = request.get_json()
    for k in ['uuid', 'hostname', 'pid']:
        if k not in data:
            abort(400)
    worker = Worker(uuid=data['uuid'],
                    hostname=data['hostname'],
                    pid=data['pid'],
                    start=datetime.now()
                    )
    db.session.add(worker)
    db.session.commit()

    return jsonify({'uuid': worker.uuid, 'id': worker.id}), 201
