# This file is part of GAE Testbed (http://gae-testbed.googlecode.com).
# 
# Copyright (C) 2009 JJ Geewax http://geewax.org/
# All rights reserved.
# 
# This software is licensed as described in the file COPYING.txt,
# which you should have received as part of this distribution.

from datastore import DataStoreTestCase
from memcache import MemcacheTestCase
from mail import MailTestCase
from taskqueue import TaskQueueTestCase

__all__ = ['UnitTestCase']

class UnitTestCase(DataStoreTestCase, MemcacheTestCase, MailTestCase, TaskQueueTestCase):
    pass
