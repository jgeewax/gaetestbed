===========
GAE Testbed
===========

.. warning::
    This documentation is currently a work in progress as the project is still
    pretty young. As more final versions of this documentation are released I
    will update this section to reflect that stability.

API Documentation
=================

Auto-generated documentation is located here: :doc:`api`

.. toctree::
    :maxdepth: 2
    :glob:
    :hidden:
    
    api

.. _tutorials:

Tutorials
=========

.. note::
    These are not completed yet! I will keep updating this page as best I can.

.. toctree::
    :maxdepth: 1
    :glob:
    
    tutorials/*

Introduction
============

Writing web apps for Google App Engine is becoming really really easy. The
App Engine team is releasing new things to make developing and deploying
applications as easy as clicking "Deploy" on the SDK Console. However building
test suites for your applications is a little bit tricky when you get into
testing that you're using the API correctly. This is where GAE Testbed comes
in.

What is it?
===========

GAE Testbed is a set of base test cases that you can mix into your regular
test cases in order to make testing the various pieces of App Engine's API
more intuitive. For example, instead of looking at the API's ``mail_stub``
internal variable has logged a message about an e-mail being sent, you can
use ``assertEmailSent()`` to make sure that in a live environment an e-mail
would be sent from your application.

.. note::
    Clearly there are limitations on what can be asserted. For example, you
    currently can't send e-mails with just `any` ``from`` address (it must
    be one of the admin's e-mails). GAE Testbed doesn't know who your admins
    are so you can't check for that sort of thing.

GAE Testbed also ensures that each test inside a test case is sandboxed from 
your other tests. That is, it makes sure the Data Store is completely empty,
and likewise for Memcache, the Task Queue, and other APIs.

Where can I get it?
===================

Stable releases of GAE Testbed are best installed via ``easy_install`` or
``pip``. This is as simple as::
    
    sudo easy_install gaetestbed

Since GAE Testbed was built to be used alongside Nose, both Nose and the
App Engine plugin for Nose (NoseGAE) are recommended. Both of these can be
installed with ``easy_install`` as well::

    sudo easy_install nose
    sudo easy_install nosegae

Finally, certain pieces of GAE Testbed (mainly the ``WebTestCase``) rely on
Ian Bicking's WebTest package, and certain things in WebTest rely on
BeautifulSoup to process HTML. All of these can be installed with 
``easy_install``::

    sudo easy_install webtest
    sudo easy_install BeautifulSoup 

How do I use it?
================

Thanks to the work by Jason Pellerin and Kumar McMillan, running tests is
incredibly simple. To pull in GAE Testbed, all you have to do is import
some of the base test cases, and mix them into your own test cases.

For example, to pull in tests that use the Data Store::

    import unittest
    
    from gaetestbed import DataStoreTestCase
    
    class MyTestCase(DataStoreTestCase, unittest.TestCase):
        def test_datastore(self):
            # Write some test code here
            pass

What else is there?
===================

I'm working on documenting GAE Testbed as fast as I can, and these docs are
definitely improving, but clearly not complete. As I continue working on them,
you can take a look at the other mixin test cases in the :doc:`api`, which
should have all the reference information you'd need about custom assert
statements and whatnot.

Also, take a look at the :ref:`tutorials` which should help you get started
in writing your first tests for you App Engine application. Finally, when in
doubt, there's always the :ref:`genindex`.

How can I help?
===============

GAE Testbed is hosted on Google Code at http://gae-testbed.googlecode.com/.
You're more than welcome to check out the source code (stored in a SVN repo)
and provide patches for new features you want, or fixes for bugs that you find.
I'll do my best to respond in a timely manner to feature requests and bug reports.

If you don't have time to write a patch but would really like a feature added,
the best place to make that request would be on the issue tracking page which
is located at http://code.google.com/p/gae-testbed/issues/.
