======================
Testing the Data Store
======================

Overview
========

This tutorial walks you through using the :ref:`datastoretestcase` from
start to finish. It creates a simple model and shows you how to use the
base test case in your tests.

Getting Started
===============

Let's take a look at a very simple application that has
nothing but a ``db.Model`` that can be saved via the command line.

``myproject/models.py``::

    from google.appengine.ext import db
    
    class Person(db.Model):
        name = db.StringProperty(required=True)
        age = db.IntegerProperty(default=18)
        
        def is_old(self):
            return age >= 80

Writing a Test
==============

Now you have a ``Person`` model and a method called ``is_old``. But how do
you know if that method is correct? Let's create a simple test that checks
that there aren't any typos or problems with our code.

``myproject/test/test_person.py``::

    import unittest
    
    from models import Person
    
    class TestPerson(unittest.TestCase):
        def test_is_old(self):
            person = Person(name='JJ', age=22)
            self.assertFalse(person.is_old())

Placating App Engine
--------------------

Also, don't forget to throw in an ``app.yaml`` file. You'll need that to 
make NoseGAE run correctly. (The ``/media/`` is just a dummy placeholder...)

``myproject/app.yaml``::

    application: myproject
    version: 1
    runtime: python
    api_version: 1
    
    handlers:
    - url: /media/
      static_dir: media

Running the Test
================

All this does is check our assumption with a positive test case. This does
cover all of the lines, but isn't really a complete suite. For now this will 
be more than enough. Let's hop to the command line and check what we've
put together::

    jj@im-jj:~$ cd myproject
    jj@im-jj:myproject$ nosetests --with-gae
    E
    ======================================================================
    ERROR: test_is_old (test_person.TestPerson)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/jjg/development/workspace/myproject/test/test_person.py", line 8, in test_is_old
        self.assertFalse(person.is_old())
      File "/Users/jjg/development/workspace/myproject/models.py", line 8, in is_old
        return age >= 80
    NameError: global name 'age' is not defined
    -------------------- >> begin captured logging << --------------------
    root: WARNING: Could not read datastore data from /var/folders/iL/iLSZb8eEE1K-cMRyPYYFpU+++TI/-Tmp-/nosegae.datastore
    root: WARNING: Could not read datastore data from /var/folders/iL/iLSZb8eEE1K-cMRyPYYFpU+++TI/-Tmp-/nosegae.datastore.history
    root: INFO: zipimporter('/Library/Python/2.5/site-packages/WebOb-0.9.7dev_r8060-py2.5.egg', '')
    root: INFO: zipimporter('/Library/Python/2.5/site-packages/setuptools-0.6c9-py2.5.egg', '')
    root: INFO: zipimporter('/Library/Python/2.5/site-packages/BeautifulSoup-3.1.0.1-py2.5.egg', '')
    root: INFO: zipimporter('/Library/Python/2.5/site-packages/NoseGAE-0.1.6-py2.5.egg', '')
    root: INFO: zipimporter('/Library/Python/2.5/site-packages/gaetestbed-0.11dev_r13-py2.5.egg', '')
    root: INFO: zipimporter('/Library/Python/2.5/site-packages/PyYAML-3.09-py2.5-macosx-10.5-i386.egg', '')
    --------------------- >> end captured logging << ---------------------
    
    ----------------------------------------------------------------------
    Ran 1 test in 0.060s
    
    FAILED (errors=1) 
    

Whoops! That's not good. Looks like we have a little type there. Go ahead and
change ``age`` to ``self.age`` and this should clear right up::

    jj@im-jj:myproject$ nosetests --with-gae
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.058s
    
    OK

Are the tests Sandboxed?
========================

Well that's nice... But we didn't even import GAE Testbed! This looks like one
big advertisement for Nose and NoseGAE. Let's make some more tests and see where
GAE Testbed comes into play.

``myproject/test/test_person.py``::

    import unittest
    
    from models import Person
    
    class TestPerson(unittest.TestCase):
        def test_is_old(self):
            person = Person(name='JJ', age=22)
            self.assertFalse(person.is_old())
    
        def test_is_empty(self):
            self.assertEqual(Person.all().count(), 0)
            
            person = Person(name='JJ', age=22)
            person.put()
            
            self.assertEqual(Person.all().count(), 1)
        
        def test_assert_empty_again(self):
            self.assertEqual(Person.all().count(), 0)
            
            person = Person(name='JJ', age=22)
            person.put()
            
            self.assertEqual(Person.all().count(), 1)

This looks pretty harmless right? Testing that at the start of each test
the Datastore doesn't have any people saved? Let's give it a try and see 
what happens::

    jj@im-jj:myproject$ nosetests --with-gae
    INFO     2009-09-29 02:15:39,371 py_zipimport.py:108] zipimporter('/Library/Python/2.5/site-packages/simplejson-2.0.9-py2.5-macosx-10.5-i386.egg', 'simplejson/')
    INFO     2009-09-29 02:15:39,451 py_zipimport.py:108] zipimporter('/Library/Python/2.5/site-packages/WebTest-1.2-py2.5.egg', 'webtest/')
    .F.
    ======================================================================
    FAIL: test_is_empty (test_person.TestPerson)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/jjg/development/workspace/myproject/test/test_person.py", line 11, in test_is_empty
        self.assertEqual(Person.all().count(), 0)
    AssertionError: 1 != 0
    
    ----------------------------------------------------------------------
    Ran 3 tests in 0.069s

    FAILED (failures=1)

Sandboxing with GAE Testbed
===========================

Why did this fail? It looks like the Data Store isn't actually empty between
tests! Now let's see what GAE Testbed can do to make these tests pass.

``myproject/test/test_person.py``::

    import unittest
    
    from gaetestbed import DataStoreTestCase
    
    from models import Person
    
    class TestPerson(DataStoreTestCase, unittest.TestCase):
        def test_is_old(self):
            person = Person(name='JJ', age=22)
            self.assertFalse(person.is_old())
    
        def test_is_empty(self):
            self.assertEqual(Person.all().count(), 0)
            
            person = Person(name='JJ', age=22)
            person.put()
            
            self.assertEqual(Person.all().count(), 1)
        
        def test_is_empty_again(self):
            self.assertEqual(Person.all().count(), 0)
            
            person = Person(name='JJ', age=22)
            person.put()
            
            self.assertEqual(Person.all().count(), 1)

Now let's try to run these again::
	
    jj@im-jj:myproject$ nosetests --with-gae
    INFO     2009-09-29 02:18:56,733 py_zipimport.py:108] zipimporter('/Library/Python/2.5/site-packages/simplejson-2.0.9-py2.5-macosx-10.5-i386.egg', 'simplejson/')
    INFO     2009-09-29 02:18:56,812 py_zipimport.py:108] zipimporter('/Library/Python/2.5/site-packages/WebTest-1.2-py2.5.egg', 'webtest/')
    ...
    ----------------------------------------------------------------------
    Ran 3 tests in 0.084s
    
    OK

Summary
=======

So what's the difference? The difference is that in the second
test case we mixed in the ``DataStoreTestCase`` provided by 
GAE Testbed which makes sure that at the start of every test the 
Data Store is cleared out and ready for a fresh test. Basically
it just makes sure that your test code runs in a sandbox each time
so you don't have to worry about the order of the tests, or if certain
tests fail, or any of that nonsense. Nice right?
