Introduction
============
The taskfarm is a server-client application that tracks tasks to be completed. The server is provides a REST API to create and update runs. This is the python server documentation.

This package solves the problem of managing a loosely coupled taskfarm where there are many tasks and the workers are entirely independent of each other. Instead of using a farmer process a database is used to hand out new tasks to the workers. The workers contact a web application via http(s) to get a new task.

You can use the `taskfarm-worker <https://github.com/mhagdorn/taskfarm-worker>`_ python package to connect to the taskfarm service.

The server is implemented using the `flask <https://flask.palletsprojects.com/>`_ web framework and uses `flask-sqlalchemy <https://flask-sqlalchemy.palletsprojects.com/>`_ to connect to a relational database.

Installation
============
Local Installation
------------------
You can install the package from source after cloning the repository

.. code-block:: bash
		
  git clone https://github.com/mhagdorn/taskfarm.git
  cd taskfarm
  python3 setup.py install

or simply using ``pip``

.. code-block:: bash
		
  pip install taskfarm

Setup
^^^^^
After installing the python package you need to connect to a database. For
testing purposes you can use sqlite. However, sqlite does not allow row
locking so if you use parallel workers a single task may get assigned to
multiple workers. For production use you should use a postgres database instead.

You can set the environment variable ``DATABASE_URL`` to configure the database
connection (see the `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls>`_). For example

.. code-block:: bash
		
 export DATABASE_URL=sqlite:///app.db

or

.. code-block:: bash

 export DATABASE_URL=postgresql://user:pw@host/db


You then need to create the tables by running

.. code-block:: bash
		
 adminTF --init-db

You can then create some users

.. code-block:: bash
		
 adminTF -u some_user -p some_password

These users are used by the worker to connect to the service.

Running the Taskfarm Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The taskfarm server is a flask web application. For testing you can run it locally using

.. code-block:: bash
		
  export FLASK_APP=taskfarm
  flask run

You can check the service is running by browsing to http://localhost:5000/ or running

.. code-block:: bash

  curl http://localhost:5000/

For a production setup you need to deploy the flask application using a WSGI server such as `gunicorn <https://gunicorn.org/>`_. The flask documentation lists the various options for self-hosting or hosting in the cloud a flask application.

Containerised Installation
--------------------------
Instead of installing the taskfarm server locally and managing the flask webapplication service you can run the taskfarm server as a containerised service. You need a working `docker setup <https://docs.docker.com/get-started/>`_ and `docker compose <https://docs.docker.com/compose/>`_. The taskfarm service is built using Ubuntu containers, one for the web application, one for the postgres database and one for the web server. You can build and start the containers using

.. code-block:: bash

  docker-compose build

You need to initialise the database and create a user, ie

.. code-block:: bash

  docker-compose run web  adminTF --init-db
  docker-compose run web  adminTF -u taskfarm -p hello
 
You can now start the service

.. code-block:: bash

  docker-compose up -d

and you can reach the taskfarm server on port 80. You can check the service is running by browsing to http://localhost/ or running

.. code-block:: bash

  curl http://localhost/
