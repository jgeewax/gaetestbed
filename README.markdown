# GAE Testbed

The full documentation for this project is located [http://gaetestbed.geewax.org/index.html](http://gaetestbed.geewax.org/index.html)

## Special note

Now that I work for Google, 20% of my time is spent porting GAE Testbed to be part of the Python SDK. As a result, don't expect many new features on this project...

## Introduction
Writing tests for AppEngine applications seems more difficult to me than it
should be. This project is a set of base test cases to make it simple to test
the more complicated pieces of !AppEngine's framework (such as sending E-mail
messages, the datastore, Memcache, etc).

### How to get it...

    $ sudo easy_install gaetestbed

### How to run it...

    $ nosetests --with-gae

## Test Showcase

Here are a few examples of how GAETestbed makes testing the complicated parts of !AppEngine really simple.

### Testing that E-mail was Sent
as seen on [StackOverflow](http://stackoverflow.com/questions/427400/unit-testing-and-mocking-email-sender-in-python-with-google-appengine/1411769#1411769)


    import unittest
    from gaetestbed import MailTestCase

    class MyTestCase(MailTestCase, unittest.TestCase):
        def test_email_sent(self):
            send_email_to('test@example.org') # Some method that sends e-mail...
            self.assertEmailSent(to='test@example.org')
            self.assertEqual(len(self.get_sent_messages()), 1)

### Testing that Memcache was Hit

    import unittest
    from gaetestbed import MemcacheTestCase

    class MyTestCase(MemcacheTestCase, unittest.TestCase):
    def test_memcache_gets_hit(self):
        self.assertMemcacheItems(0)
        self.assertMemcacheHits(0)
        
        add_to_memcache('something', 'something') # Add something to memcache somehow...
        self.assertMemcacheItems(1)
        self.assertMemcacheHits(0)
        
        get_page('/page_that_hits_memcache/')
        self.assertMemcacheItems(1)
        self.assertMemcacheHits(1)

### Testing that Tasks were added to the Task Queue

    import unittest
    from gaetestbed import TaskQueueTestCase

    class MyTestCase(TaskQueueTestCase, unittest.TestCase):
        def test_taskqueue(self):
            # Check that nothing is in the queue
            self.assertTasksInQueue(0)
            
            # Add something to a Queue
            add_to_taskqueue(url='/worker/dummy/')
            
            # Checks that there are things in the queue
            self.assertTasksInQueue()
            
            # Checks exactly one item in the queue
            self.assertTasksInQueue(1)
            
            # Checks that 1 item with the specified URL is in the queue
            self.assertTasksInQueue(1, url='/worker/dummy/')

### Testing that stuff was saved to the Datastore
(Most of this is provided thanks to NoseGAE.)

    import unittest
    from gaetestbed import DataStoreTestCase
    from myproject.models import MyModel

    class MyTestCase(DataStoreTestCase, unittest.TestCase):
        def test_datastore_gets_hit(self):
            self.assertEqual(MyModel.all().count(), 0)
            
            MyModel(name='Name').put()
            self.assertEqual(MyModel.all().count(), 1)
        
        def test_datastore_still_empty(self):
            self.assertEqual(MyModel.all().count(), 0)

### Optimization testing, test number of DataStore queries

    from __future__ import with_statement
    import unittest
    from gaetestbed import DataStoreTestCase
    from myproject.models import MyModel

    class MyTestCase(DataStoreTestCase, unittest.TestCase):
        def test_num_queries(self):
            self.assertEqual(MyModel.all().count(), 0)
            
            # Check that no more than 1 query is run in this block of code
            with self.max_queries(1):
                MyModel(name='Name').put()
        
        def test_query_count(self):
            self.assertEqual(MyModel.all().count(), 0)
            
            MyModel(name='Name').put()
            self.assertEqual(MyModel.all().count(), 1)
            
            # Check that the number of queries total for this test case is under 100
            self.assertTrue(self.query_count < 100)

### Web Testing
(Most of this is provided thanks to WebTest.)

    import unittest
    from gaetestbed import WebTestCase, DataStoreTestCase
    from handlers import application # (application should be a WSGI app)

    class MyTestCase(WebTestCase, DataStoreTestCase, unittest.TestCase):
        APPLICATION = application
        
        def test_get_redirects(self):
            response = self.get('/')
            self.assertRedirects(response)
        
        def test_post_creates_model(self):
            self.assertEqual(MyModel.all().count(), 0)
            
            data = {'name': 'Name'}
            response = self.post('/create-my-model/', data=data)
            self.assertRedirects(response)
            self.assertEqual(MyModel.all().count(), 1)
        
        def test_get_with_cookie(self):
            response = self.get('/')
            self.assertRedirects(response)
            
            self.set_cookie('session_id', 'secret')
            response = self.get('/')
            self.assertOK(response)
        
        def test_cookies_cleared_between_tests(self):
            session_id = self.get_cookie('session_id')
            self.assertEqual(session_id, None)

### Mixing them All together
#### A "Unit" test case
`UnitTestCase` has all of the basics except `WebTestCase`. This makes it useful
for testing your models and library methods.

    import unittest
    from gaetestbed import UnitTestCase
    from myproject.models import MyModel

    class MyTestCase(UnitTestCase, unittest.TestCase):
        def test_memcache_gets_hit(self):
            self.assertMemcacheHits(0)
        
        def test_datastore_gets_hit(self):
            MyModel(name='Name').put()
            self.assertEqual(MyModel.all().count(), 1)
        
        def test_email_sent(self):
            # (Send an e-mail)
            self.assertEmailSent()

#### A "Functional" test case
`FunctionalTestCase` has everything the `UnitTestCase` does, with the addition
of `WebTestCase` for testing web interactions using !WebTest.

    import unittest
    from gaetestbed import FunctionalTestCase
    from myproject.models import MyModel
    from handlers import application # (application should be a WSGI app)

    class MyTestCase(FunctionalTestCase, unittest.TestCase):
        APPLICATION = application
        
        def test_memcache_gets_hit(self):
            self.assertMemcacheHits(0)
        
        def test_datastore_gets_hit(self):
            MyModel(name='Name').put()
            self.assertEqual(MyModel.all().count(), 1)
        
        def test_email_sent(self):
            # (Send an e-mail)
            self.assertEmailSent()
        
        def test_get_redirects(self):
            response = self.get('/')
            self.assertRedirects(response)
        
        def test_post_creates_model(self):
            self.assertEqual(MyModel.all().count(), 0)
            
            data = {'name': 'Name'}
            response = self.post('/create-my-model/', data=data)
            self.assertRedirects(response)
            self.assertEqual(MyModel.all().count(), 1)

## Dependencies
This set of cases was designed to run with [NoseGAE](http://code.google.com/p/nose-gae/),
so to run the tests that way you'll probably want to download an install it.
Additionally, to run the functional (web) tests, you'll need to grab
[WebTest](http://pythonpaste.org/webtest/). Both of these are easy-installable:


    $ sudo easy_install nose
    $ sudo easy_install nosegae
    $ sudo easy_install webtest

## Benefits
 * Each test is sandboxed so that you can assume all of the services are empty
   when you start your test. This way, there's no need to worry about cleaning
   up data between tests.
 * Helper assert methods that simplify testing such as `assertMailSent()` or
   `assertMemcacheHits()`

## Feedback, etc
 * If you find a bug with the testbed, open a ticket [here](http://github.com/jgeewax/gaetestbed/issues).
   All tickets are really appreciated.
 * If there's already a ticket that you'd like to see done faster, star the ticket
   and it will get more attention. Patches are always appreciated too :)

## Thanks
 * Thanks for Jason Pellerin and Kumar McMillan for their work on Nose and NoseGAE.
 * Thanks to Ian Bicking for his work on WebTest

