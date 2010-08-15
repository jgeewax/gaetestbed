# This file is part of GAE Testbed (http://github.com/jgeewax/gaetestbed).
# 
# Copyright (C) 2009 JJ Geewax http://geewax.org/
# All rights reserved.
# 
# This software is licensed as described in the file COPYING.txt,
# which you should have received as part of this distribution.

class BaseTestCase(object):
    """
    BaseTestCase is the base mixin test case that holds common
    assert methods to be used across all test cases.
    """
    def assertLength(self, iterable, count):
        """
        Assert that an `iterable` is of a given length.
        
        This is useful when you don't care about the type of the iterable, 
        but just care that it is a certain length. If the item provided
        doesn't have the expected length, or the length cannot be determined,
        the test will fail.
        
        This will first try to call ``item.count()`` (assuming it's a ``QuerySet``)
        and then try ``len(item)``.
        
        Let's take a look at an example::
            
            class TestCase(BaseTestCase, unittest.TestCase):
                def test_length(self):
                    # This will call len('asdf')
                    self.assertLength('asdf', 4)
                    
                    # This will use .count()
                    self.assertLength(models.MyModel.all(), 0)
                    
                    # These will use len()
                    self.assertLength([0, 1, 2], 3)
                    self.assertLength((), 0)
                    
                    # This will fail
                    self.assertLength(7, 0)
        """
        length = None
        
        if length is None:
            try: length = iterable.count()
            except: pass
        
        if length is None:
            try: length = len(iterable)
            except: pass
        
        if length is None:
            self.fail("Unable to get length for object %s" % type(iterable))
        
        else:
            self.assertEqual(length, count)
