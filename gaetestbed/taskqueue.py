# This file is part of GAE Testbed (http://gae-testbed.googlecode.com).
# 
# Copyright (C) 2009 JJ Geewax http://geewax.org/
# All rights reserved.
# 
# This software is licensed as described in the file COPYING.txt,
# which you should have received as part of this distribution.

import base64

from google.appengine.api import apiproxy_stub_map

from base import BaseTestCase

__all__ = ['TaskQueueTestCase']

class TaskQueueTestCase(BaseTestCase):
    """
    """
    
    # This is the format usable with strftime/strptime for parsing the
    # ``eta`` field for a particular task
    TASK_ETA_FORMAT = "%Y/%m/%d %H:%M:%S"
    
    def setUp(self):
        """
        """
        super(TaskQueueTestCase, self).setUp()
        self.clear_task_queue()
    
    def assertTasksInQueue(self, n=None, url=None, name=None, queue_names=None):
        """
        """
        tasks = self.get_tasks(url=url, name=name, queue_names=queue_names)
        
        if n is None:
            self.assertNotEqual(len(tasks), 0)
        else:
            self.assertLength(tasks, n)
    
    def clear_task_queue(self):
        """
        """
        stub = self.get_task_queue_stub()
        for name in self.get_task_queue_names():
            stub.FlushQueue(name)
    
    def get_tasks(self, url=None, name=None, queue_names=None):
        """
        """
        tasks = []
        stub = self.get_task_queue_stub()
        
        for queue_name in queue_names or self.get_task_queue_names():
            tasks.extend(stub.GetTasks(queue_name))
        
        if url is not None:
            tasks = [t for t in tasks if t['url'] == url]
        
        if name is not None:
            tasks = [t for t in tasks if t['name'] == name]
        
        for task in tasks:
            params = {}
            decoded_body = base64.b64decode(task['body'])
            
            if decoded_body:
                # urlparse.parse_qs doesn't seem to be in Python 2.5...
                params = dict([item.split('=', 2) for item in decoded_body.split('&')])
            
            task.update({
                'decoded_body': decoded_body,
                'params': params,
            })
            
            # These lines have to remain commented out as (for some reason) the strptime() call
            # throws a SystemError: Parent module 'gaetestbed' not loaded
            # This looks to be an issue with NoseGAE's sandboxing (--without-sandbox doesn't throw the error)
            #
            #if task.get('eta'):
            #    task['eta_datetime'] = datetime.strptime(task['eta'], "%Y/%m/%d %H:%M:%S")
            #    task['eta_date'] = task['eta_datetime'].date()
            #    task['eta_time'] = task['eta_datetime'].time()
            #
            #else:
            #    task.update({
            #        'eta_datetime': None,
            #        'eta_date':     None,
            #        'eta_time':     None,
            #    })
        
        return tasks
    
    def get_task_queues(self):
        """
        """
        return self.get_task_queue_stub().GetQueues()
    
    def get_task_queue_names(self):
        """
        """
        return [q['name'] for q in self.get_task_queues()]
    
    def get_task_queue_stub(self):
        """
        """
        return apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map['taskqueue']
    
