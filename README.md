taskfarm
========
This package solves the problem of managing a loosely coupled taskfarm where
there are many tasks and the workers are entitrly independent of each other.
Instead of using a farmer process a database is used to hand out new tasks to
the workers. The workers contact a web application via http(s) to get a new
task.

You can use the [taskfarm-worker](https://github.com/mhagdorn/taskfarm-worker)
to connect to the taskfarm service.

See the [documentation](https://taskfarm.readthedocs.io/en/latest/) for installation instructions.

![test package taskfarm](https://github.com/mhagdorn/taskfarm/workflows/test%20package%20taskfarm/badge.svg) [![Documentation Status](https://readthedocs.org/projects/taskfarm/badge/?version=latest)](https://taskfarm.readthedocs.io/en/latest/?badge=latest) [![CITATION.cff](https://github.com/mhagdorn/taskfarm/actions/workflows/cff-validator.yml/badge.svg)](https://github.com/mhagdorn/taskfarm/actions/workflows/cff-validator.yml)

