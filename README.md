taskfarm
========
This package solves the problem of managing a loosely coupled taskfarm where
there are many tasks and the workers are entitrly independent of each other.
Instead of using a farmer process a database is used to hand out new tasks to
the workers. The workers contact a web application via http(s) to get a new
task.

You can use the [taskfarm-worker](https://github.com/mhagdorn/taskfarm-worker)
to connect to the taskfarm service.

Setup
-----
After installing the python package you need to connect to a database. For
testing purposes you can use sqlite. However, sqlite does not allow row
locking so if you use parallel workers a task may get assigned to the multiple
workers.

You can set the environment variable DATABASE_URL to configure the data base
connection. For example
```
export DATABASE_URL=sqlite:///app.db
```
or
```
export DATABASE_URL=postgresql://user:pw@host/db
```

You then need to create the tables by running
```
adminTF --init-db
```
You can then create some users
```
adminTF -u some_user -p some_password
```
These users are used by the worker to connect to the service.

![test package taskfarm](https://github.com/mhagdorn/taskfarm/workflows/test%20package%20taskfarm/badge.svg) [![Documentation Status](https://readthedocs.org/projects/taskfarm/badge/?version=latest)](https://taskfarm.readthedocs.io/en/latest/?badge=latest)

