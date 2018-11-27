taskfarm
========
This package solves the problem of managing a loosely coupled taskfarm where
there are many tasks and the workers are entitrly independent of each other.
Instead of using a farmer process a database is used to hand out new tasks to
the workers. The workers contact a web application via http(s) to get a new
task.