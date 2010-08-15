# This file is part of GAE Testbed (http://github.com/jgeewax/gaetestbed).
# 
# Copyright (C) 2009 JJ Geewax http://geewax.org/
# All rights reserved.
# 
# This software is licensed as described in the file COPYING.txt,
# which you should have received as part of this distribution.

from google.appengine.api import memcache

from base import BaseTestCase

__all__ = ['MemcacheTestCase']

class MemcacheTestCase(BaseTestCase):
    """
    The ``MemcacheTestCase`` is a base test case that provides helper methods
    for dealing with App Engine's Memcache API.
    
    App Engine actually does most of the work for this by providing statistics
    through the Memcache API, as well as a simple method call to clear out the
    cache.
    
    The main feature of this is the ability to assert that items are in the
    cache, and to check the number of hits to the cache. More fine grained
    assertions are on the way, for now it's pretty general, only able to assert
    that things are in there and not which specific things.
    
    The following example illustrates a simple way of checking that Memcache is
    working as expected::
    
        import unittest
        
        from gaetestbed import MemcacheTestCase
        
        from google.appengine.api import memcache
        
        class MyTestCase(MemcacheTestCase, unittest.TestCase):
            def test_memcache(self):
                # Nothing has been put in the cache, or retrieved from the cache
                self.assertMemcacheItems(0)
                self.assertMemcacheHits(0)
                
                # Add something to the cache
                memcache.set(key='test_item', value='test_content')
                
                # One item added, no hits yet
                self.assertMemcacheItems(1)
                self.assertMemcacheHits(0)
                
                # Grab it from the cache:
                item = memcache.get('test_item')
                
                # One item, one hit
                self.assertMemcacheItems(1)
                self.assertMemcacheHits(1)
    
    Just like the other test cases, each test should be a sandbox, meaning that the
    following assertions should pass if they are run at the start of every test case::
    
        self.assertMemcacheItems(0)
        self.assertMemcacheHits(0)
    """
    def setUp(self):
        """
        This method is called at the start of each test case.
        
        If you need to use this method for your own test set up, make sure
        that you call ``super()``. If not, the cache may not be emptied
        properly and your tests might not be properly sandboxed.
        
        Here is an example of how to properly override the ``setUp`` method::
        
            import unittest
            
            from gaetestbed import MemcacheTestCase
            
            class MyTestCase(MemcacheTestCase, unittest.TestCase):
                def setUp(self):
                    super(MyTestCase, self).setUp()
                    # Do anything else you need here
        """
        super(MemcacheTestCase, self).setUp()
        self.clear_memcache()
    
    def clear_memcache(self):
        """
        Empties the cache of all its content.
        
        This method is called at the start of every test in order to ensure that
        each test is fully sandboxed from the others, though you're free to call
        it elsewhere in your tests as you need::
        
            import unittest
            
            from gaetestbed import MemcacheTestCase
            
            from google.appengine.api import memcache
            
            class MyTestCase(MemcacheTestCase, unittest.TestCase):
                def test_memcache(self):
                    # Check that the cache starts empty
                    self.assertMemcacheItems(0)
                    
                    # Add something to the cache, check that it was added
                    memcache.set(key='test_item', value='test_content')
                    self.assertMemcacheItems(1)
                    
                    # Clear the cache, check that it's now empty
                    self.clear_memcache()
                    self.assertMemcacheItems(0)
        """
        memcache.flush_all()
    
    def assertMemcacheHits(self, hits):
        """
        Asserts that the Memcache API has been hit exactly ``hits`` times.
        
        This method checks the statistics for the cache and asserts that the
        cache has had a certain number of successful hits. If a request is
        not in the cache (cache miss) the number of hits should not change.
        
        For example::
        
            import unittest
            
            from gaetestbed import MemcacheTestCase
            
            from google.appengine.api import memcache
            
            class MyTestCase(MemcacheTestCase, unittest.TestCase):
                def test_memcache(self):
                    # Nothing has retrieved from the cache
                    self.assertMemcacheHits(0)
                    
                    # Add something to the cache
                    memcache.set(key='test_item', value='test_content')
                    
                    # Test still no hits
                    self.assertMemcacheHits(0)
                    
                    # Grab it from the cache:
                    item = memcache.get('test_item')
                    
                    # Assert that there was a cache hit
                    self.assertMemcacheHits(1)
                    
                    # Grab something that doesn't exist
                    memcache.get('bad_key')
                    
                    # Assert that still one hit
                    self.assertMemcacheHits(1)
        """
        self.assertEqual(memcache.get_stats()['hits'], hits)
    
    def assertMemcacheItems(self, items):
        """
        Asserts that the Memcache API contains exactly ``items`` items.
        
        This method checks the statistics for the cache and asserts that the
        there are a certain number of items stored in the cache.
        
        For example::
        
            import unittest
            
            from gaetestbed import MemcacheTestCase
            
            from google.appengine.api import memcache
            
            class MyTestCase(MemcacheTestCase, unittest.TestCase):
                def test_memcache(self):
                    # Nothing has been added to the cache
                    self.assertMemcacheItems(0)
                    
                    # Add something to the cache
                    memcache.set(key='test_item', value='test_content')
                    
                    # Test that the item was added
                    self.assertMemcacheItems(1)
                    
                    # Remove that key
                    memcache.delete('test_item')
                    
                    # Test that the cache has zero items
                    self.assertMemcacheHits(0)
        """
        self.assertEqual(memcache.get_stats()['items'], items)
