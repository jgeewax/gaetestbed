# This file is part of GAE Testbed (http://github.com/jgeewax/gaetestbed).
# 
# Copyright (C) 2009 JJ Geewax http://geewax.org/
# All rights reserved.
# 
# This software is licensed as described in the file COPYING.txt,
# which you should have received as part of this distribution.
import webtest

from base import BaseTestCase

__all__ = ['WebTestCase']

class WebTestCase(BaseTestCase):
    APPLICATION = None
    
    def get_application(self):
        if not hasattr(self, '_app'):
            self._app = None
        
        if not self._app and self.APPLICATION:
            self._app = webtest.TestApp(self.APPLICATION)
        
        error = 'Missing class variable APPLICATION'
        self.assertTrue(self._app is not None, error)
        
        return self._app
    
    app = property(get_application)
    
    def assertRedirects(self, response, to=None):
        """
        Asserts that a response from the test web server (using `get` or `post)
        returns a 301 or 302 status. 
        
        This assertion would fail if you expect the page to redirect and instead
        the server tells the browser that there was a 500 error, or some other
        non-redirecting status code.
        
        For example::
        
            import unittest
            
            from gaetestbed import WebTestCase
            
            from my_handlers.some_handler import application
            
            class MyTestCase(WebTestCase, unittest.TestCase):
                APPLICATION = application
                
                def test_redirects(self):
                    response = self.get('/page_that_redirects/')
                    self.assertRedirects(response)
                
                def test_redirects_but_errors(self):
                    response = self.get('/page_with_exception/')
                    
                    # This would fail if the page throws an exception:
                    self.assertRedirects(response)
        """
        error = 'Response did not redirect (status code was %i).' % response.status_int
        self.assertTrue(response.status_int in (301, 302), error)
        if to is not None:
            error = 'Response redirected, but went to %s instead of %s' % (
                response.location, to
            )
            self.assertEqual(response.location, 'http://localhost%s' % to, error)
    
    def assertOK(self, response):
        """
        Asserts that a response from the test web server (using `get` or
        `post`) returns a 200 OK status code. 
        
        This assertion would fail if you expect a standard page to be returned
        and instead the server tells the browser to redirect elsewhere.
        
        For example::
        
            import unittest
            
            from gaetestbed import WebTestCase
            
            from my_handlers.some_handler import application
            
            class MyTestCase(WebTestCase, unittest.TestCase):
                APPLICATION = application
                
                def test_ok(self):
                    response = self.get('/')
                    self.assertOK(response)
                
                def test_ok_with_redirect(self):
                    response = self.get('/page_that_redirects/')
                    
                    # This would fail if the page redirects:
                    self.assertOK(response)
        """
        error = 'Response did not return a 200 OK (status code was %i)' % response.status_int
        return self.assertEqual(response.status_int, 200, error)
    
    def assertNotFound(self, response):
        error = 'Response was found (status code was %i)' % response.status_int
        return self.assertEqual(response.status_int, 404, error)
    
    def assertForbidden(self, response):
        error = 'Response was allowed (status code was %i)' % response.status_int
        return self.assertEqual(response.status_int, 403, error)
    
    def get(self, *args, **kwargs):
        if 'status' not in kwargs:
            kwargs['status'] = '*'
        return self.app.get(*args, **kwargs)
    
    def post(self, url, data, *args, **kwargs):
        data = self.url_encode(data)
        if 'status' not in kwargs:
            kwargs['status'] = '*'
        return self.app.post(url, data, *args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if 'status' not in kwargs:
            kwargs['status'] = '*'
        return self.app.delete(*args, **kwargs)
    
    def put(self, *args, **kwargs):
        if 'status' not in kwargs:
            kwargs['status'] = '*'
        return self.app.put(*args, **kwargs)
    
    def url_encode(self, data):
        if isinstance(data, dict):
            items = []
            for k, v in data.copy().items():
                if isinstance(v, (list, tuple)):
                    for item in v:
                        items.append('%s=%s' % (k, item))
                else:
                    items.append('%s=%s' % (k, v))
            
            data = '&'.join(items)
        
        return data
    
    def get_cookie(self, key):
        return self.app.cookies.get(key)
    
    def set_cookie(self, key, value):
        self.app.cookies[key] = value
