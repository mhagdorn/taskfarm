Taskfarm REST API
===================
.. qrefflask:: taskfarm:app
   :undoc-static:

.. autoflask:: taskfarm:app
   :endpoints:
   :undoc-static:
   :order: path

.. http:get:: /api/runs/(string:uuid)

   get information about a particular run

   :param uuid: uuid of the run
   :type uuid: string
   :query info: request particular information about the run.
   :status 404: when the run does not exist
   :status 404: when unkown information is requested
   :status 200: the call successfully returned a json string

   The ``info`` query parameter can be one of ``percentDone``, ``numWaiting``, ``numDone``, ``numComputing`` to get particular information of the run. By default ``info`` is the empty string and call returns a json object containing all those pieces of information.

.. http:delete:: /api/runs/(string:uuid)

   delete a particular run

   :param uuid: uuid of the run
   :type uuid: string
   :status 404: when the run does not exist
   :status 204: when the run was successfully deleted

.. http:get:: /api/runs/(string:uuid)/tasks/(int:taskID)

   get information about a particular task

   :param uuid: uuid of the run
   :type uuid: string
   :param taskID: the task's ID
   :type taskID: int
   :query info: request particular information about the task
   :status 404: when the run does not exist
   :status 404: when the taskID < 0 or when taskID is larger than the number of tasks
   :status 404: when unkown information is requeste
   :status 200: the call successfully returned a json string

   The ``info`` query parameter can be one of ``status`` or ``percentDone`` to get particular information of the task. By default ``info`` is the empty string and call returns a json object containing all those pieces of information.
   
.. http:put:: /api/runs/(string:uuid)/tasks/(int:taskID)

   update a particular task

   :param uuid: uuid of the run
   :type uuid: string
   :param taskID: the task's ID
   :type taskID: int

   :<json float percentCompleted: percentage of task completed
   :<json string status: status of task, can be ``waiting``, ``computing``, ``done``

   :status 400: an error occurred updating the task
   :status 204: the task was successfully updated
