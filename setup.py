# This file is part of GAE Testbed (http://gae-testbed.googlecode.com).
# 
# Copyright (C) 2009 JJ Geewax http://geewax.org/
# All rights reserved.
# 
# This software is licensed as described in the file COPYING.txt,
# which you should have received as part of this distribution.

from setuptools import setup, find_packages
import sys, os

version = '0.12'

setup(
    name='gaetestbed',
    version=version,
    description="GAE Testbed is a set of test cases to simplify testing on AppEngine",
    long_description="""\
    This library provides a set of base test cases that can be mixed into your existing test cases.
    
    They provide additional features to sandbox each test (by clearing the DataStore, Memcache, etc)
    and also add in additional `assert` style statements.
    
    MailTestCase example::
        
        import unittest
        from gaetestbed import MailTestCase
        
        class MyTestCase(unittest.TestCase, MailTestCase):
            def test_email_sent(self):
                send_email_to('test@example.org') # Some method that sends e-mail...
                self.assertEmailSent(to='test@example.org')
                self.assertEqual(len(self.get_sent_messages()), 1)
    
    MemcacheTestCase example::
    
        import unittest
        from gaetestbed import MemcacheTestCase
        
        class MyTestCase(unittest.TestCase, MemcacheTestCase):
            def test_memcache_gets_hit(self):
                self.assertMemcacheItems(0)
                self.assertMemcacheHits(0)
                
                add_to_memcache('something', 'something') # Add something to memcache somehow...
                self.assertMemcacheItems(1)
                self.assertMemcacheHits(0)
                
                get_page('/page_that_hits_memcache/')
                self.assertMemcacheItems(1)
                self.assertMemcacheHits(1)
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='test testing app-engine google-app-engine gae unittest',
    author='JJ Geewax',
    author_email='jj@geewax.org',
    url='http://github.com/jgeewax/gaetestbed/downloads',
    license='GPL v2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[],
)
