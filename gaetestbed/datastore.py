# This file is part of GAE Testbed (http://github.com/jgeewax/gaetestbed).
# 
# Copyright (C) 2009 JJ Geewax http://geewax.org/
# All rights reserved.
# 
# This software is licensed as described in the file COPYING.txt,
# which you should have received as part of this distribution.

from google.appengine.api import apiproxy_stub_map, datastore_file_stub
from google.appengine.ext import db

from base import BaseTestCase

__all__ = ['DataStoreTestCase']

class DataStoreTestCase(BaseTestCase):
    """
    The ``DataStoreTestCase`` is a base test case that provides helper
    methods for dealing with ``db.Model``'s.
    
    The main thing that this mixin does is ensure that the local Data Store
    is empty at the start of each test. This way you never have to worry about
    cleaning up after previous ran tests. This becomes especially important
    when you're unsure of the order in which the tests will run.
    
    For example::
    
        import unittest
        
        from gaetestbed import DataStoreTestCase
        
        class MyTestCase(DataStoreTestCase, unittest.TestCase):
            def test_empty(self):
                self.assertLength(models.MyModel.all(), 0)
                models.MyModel(field="value").put()
                self.assertLength(models.MyModel.all(), 1)
            
            def test_still_empty(self):
                self.assertLength(models.MyModel.all(), 0)
                models.MyModel(field="value").put()
                self.assertLength(models.MyModel.all(), 1)
    
    If the Data Store wasn't emptied out between tests, one of these two 
    would fail. When you inherit from the ``DataStoreTestCase``, each test
    is run inside its own little sandbox.
    
    Keep in mind that this test case uses the ``setUp()`` method to ensure
    the Data Store is empty between tests. So if you override that in your
    test case, make sure to call super::

        import unittest
        
        from gaetestbed import DataStoreTestCase
        
        class MyTestCase(DataStoreTestCase, unittest.TestCase):
            def setUp(self):
                # Note that you're calling super on MyTestCase, not
                # on DataStoreTestCase!
                super(MyTestCase, self).setUp()
                # Do anything else you want here
            
            def test_sample(self):
                self.assertLength(models.MyModel.all(), 0)
                models.MyModel(field="value").put()
                self.assertLength(models.MyModel.all(), 1)
    """
    def setUp(self):
        """
        This method is called at the start of each test case.
        
        As noted above, if your test case needs to call ``setUp``, make
        sure to call ``super()``! Otherwise the Data Store might not be
        set up correctly.
        """
        super(DataStoreTestCase, self).setUp()
        self.clear_datastore()
    
    def _get_datastore_stub(self):
        return apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map['datastore_v3']
        
    def clear_datastore(self):
        """
        Clear the Data Store of all its data.
        
        This method can be used inside your tests to clear the Data Store mid-test.
        
        For example::
        
            import unittest
            
            from gaetestbed import DataStoreTestCase
            
            class MyTestCase(DataStoreTestCase, unittest.TestCase):
                def test_clear_datastore(self):
                    # Add something to the Data Store
                    models.MyModel(field="value").put()
                    self.assertLength(models.MyModel.all(), 1)
                    
                    # And then empty the Data Store
                    self.clear_datastore()
                    self.assertLength(models.MyModel.all(), 0)
        """
        self._get_datastore_stub().Clear()
    
    def max_queries(self, max_queries):
        """
        Provides a context manager to ensure only a certain number of queries
        are run for a given block of code.
        
        Perhaps this is best illustrated with an example::
        
            from __future__ import with_statement
            
            import unittest
            
            from gaetestbed import DataStoreTestCase
            
            class MyTestCase(DataStoreTestCase, unittest.TestCase):
                def test_clear_datastore(self):
                    with self.max_queries(2):
                        models.MyModel(field="value").put()
                        self.assertLength(models.MyModel.all(), 1)
                    
                    with self.max_queries(5):
                        # Something that might take up to five queries
                        pass
        
        In this example, if the code block inside the ``with`` statement executes
        greater that 2 (or 5 in the second block) queries, the test will fail.
        
        This can be incredibly useful for making sure that you don't accidentally tweak
        a method call and suddenly it consumes resources far beyond what you'd expected.
        
        If you only care that a certain number of queries is run throughout the entire
        test, you could add ``self.assertTrue(self.query_count < 10)`` at the end of
        your test.
        """
        return self._QueryCounter(self, max_queries)
    
    class _QueryCounter(object):
        def __init__(self, test_case, maximum_queries=None):
            self.test_case = test_case
            self.maximum_queries = maximum_queries
        
        def __enter__(self):
            self.starting_queries = self.test_case.query_count
        
        def __exit__(self, *args, **kwargs):
            num_queries_run = self.test_case.query_count - self.starting_queries
            if num_queries_run > self.maximum_queries:
                self.test_case.fail("Too many queries run: expected %d (max) got %d." % (self.maximum_queries, num_queries_run))
    
    @property
    def query_count(self):
        """
        The number of queries executed so far in the test.
        
        This method will keep track of the number of queries on a per-test
        basis. Since the Data Store is cleared out after each test, the number
        of queries resets to zero after each test.
        
        If you care how many queries a certain block of code executes, take a look
        at how to use ``max_queries()`` along with the ``with`` statement.
        
        Example::
        
            import unittest
            
            from gaetestbed import DataStoreTestCase
            
            class MyTestCase(DataStoreTestCase, unittest.TestCase):
                def test_clear_datastore(self):
                    # No queries have been run yet
                    self.assertEqual(self.query_count, 0)
                    
                    # Run one query to count the number of models
                    self.assertLength(models.MyModel.all(), 1)
                    
                    # Check that one query was run
                    self.assertEqual(self.query_count, 1)
        """
        count = 0
        queries = self._get_datastore_stub().QueryHistory()
        for n in queries.itervalues():
            count += n
        return count
