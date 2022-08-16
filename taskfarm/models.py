__all__ = ['TaskState', 'User', 'Run', 'Task', 'Worker']

from .application import db, app
from authlib.jose import jwt
from authlib.jose.errors import DecodeError
from sqlalchemy import func
import enum
from passlib.apps import custom_app_context as pwd_context


class TaskState(enum.Enum):
    waiting = 1
    computing = 2
    done = 3


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self):
        return jwt.encode(
            {'alg': 'HS256'}, {'id': self.id}, app.config['SECRET_KEY'])

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except DecodeError:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class Run(db.Model):
    __tablename__ = 'runs'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, index=True, unique=True)
    nextTask = db.Column(db.Integer, default=0)
    numTasks = db.Column(db.Integer)

    tasks = db.relationship("Task", backref='run', lazy='dynamic')

    @property
    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "numTasks": self.numTasks,
        }

    @property
    def full_status(self):
        info = self.to_dict
        for k in ['percentDone', 'numWaiting', 'numDone', 'numComputing']:
            info[k] = getattr(self, k)
        return info

    @property
    def numListedTasks(self):
        return Task.query.filter_by(run_id=self.id).count()

    @property
    def percentDone(self):
        try:
            return db.session.query(
                func.sum(Task.percentCompleted)).filter_by(
                    run_id=self.id).scalar() / self.numTasks
        except Exception:
            return 0.

    def runStatus(self, status):
        return Task.query.filter_by(run_id=self.id, status=status).count()

    @property
    def numWaiting(self):
        return self.runStatus(TaskState.waiting)

    @property
    def numDone(self):
        return self.runStatus(TaskState.done)

    @property
    def numComputing(self):
        return self.runStatus(TaskState.computing)


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Integer)
    status = db.Column(db.Enum(TaskState, validate_strings=True),
                       default=TaskState.waiting)
    started = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    percentCompleted = db.Column(db.Float, default=0.)

    run_id = db.Column(db.Integer, db.ForeignKey('runs.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))

    @property
    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task,
            "percentCompleted": self.percentCompleted,
            "status": self.status.name,
        }


class Worker(db.Model):
    __tablename__ = 'workers'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, index=True, unique=True)
    hostname = db.Column(db.String)
    pid = db.Column(db.Integer)
    start = db.Column(db.DateTime)

    tasks = db.relationship("Task", backref='worker', lazy='dynamic')

    def __repr__(self):
        return (f'{{uuid: {self.uuid}, hostname: {self.hostname}, '
                f'pid: {self.pid}, start {self.start}}}')
