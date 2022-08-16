Introduction
============
The taskfarm is a server-client application that tracks tasks to be completed. The server is provides a REST API to create and update runs. This is the python server documentation.

This package solves the problem of managing a loosely coupled taskfarm where there are many tasks and the workers are entirely independent of each other. Instead of using a farmer process a database is used to hand out new tasks to the workers. The workers contact a web application via http(s) to get a new task.

You can use the `taskfarm-worker <https://github.com/mhagdorn/taskfarm-worker>`_ python package to connect to the taskfarm service.

The server is implemented using the `flask <https://flask.palletsprojects.com/>`_ web framework and uses `flask-sqlalchemy <https://flask-sqlalchemy.palletsprojects.com/>`_ to connect to a relational database.
