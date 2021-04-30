Introduction
============
The taskfarm is a server-client application that tracks tasks to be completed. The server is provides a REST API to create and update runs. This is the python server documentation.

This package solves the problem of managing a loosely coupled taskfarm where there are many tasks and the workers are entitrly independent of each other. Instead of using a farmer process a database is used to hand out new tasks to the workers. The workers contact a web application via http(s) to get a new task.

Setup
-----
After installing the python package you need to connect to a database. For
testing purposes you can use sqlite. However, sqlite does not allow row
locking so if you use parallel workers a task may get assigned to the multiple
workers. For production use you should use a postgres database instead.

You can set the environment variable ``DATABASE_URL`` to configure the database
connection. For example

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
