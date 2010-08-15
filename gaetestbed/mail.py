# This file is part of GAE Testbed (http://github.com/jgeewax/gaetestbed).
# 
# Copyright (C) 2009 JJ Geewax http://geewax.org/
# All rights reserved.
# 
# This software is licensed as described in the file COPYING.txt,
# which you should have received as part of this distribution.

from google.appengine.api import apiproxy_stub_map, mail_stub

from base import BaseTestCase

__all__ = ['MailTestCase']

class MailTestCase(BaseTestCase):
    """
    The ``MailTestCase`` is a base test case that provides helper methods
    for dealing with App Engine's Mail API.
    
    The main feature of this test case is the ability to assert that an e-mail
    message would be sent using the Mail API calls.
    
    The following example sends an e-mail with App Engine's Mail API and then 
    tests that the e-mail was actually sent::
    
        import unittest
        
        from gaetestbed import MailTestCase
        
        from google.appengine.api import mail
        
        class MyTestCase(MailTestCase, unittest.TestCase):
            def test_email_sent(self):
                mail.send_mail(
                    to = 'test@example.org',
                    subject = 'Test E-mail',
                    sender = 'me@example.org',
                    body = 'This is a test e-mail',
                )
                
                # This will fail if an e-mail wasn't sent.
                self.assertEmailSent()
    
    Keep in mind that this isn't actually going to send an e-mail message
    to that recipient. This just checks that the call was made to App Engine's
    API stub without mocking out a call to send_mail.
    
    That is, you can send an e-mail using the ``mail.EmailMessage`` object::
    
        import unittest
        
        from gaetestbed import MailTestCase
        
        from google.appengine.api import mail
        
        class MyTestCase(MailTestCase, unittest.TestCase):
            def test_email_sent(self):
                mail.EmailMessage(
                    to = 'test@example.org',
                    subject = 'Test E-mail',
                    sender = 'me@example.org',
                    body = 'This is a test e-mail',
                ).send()
                
                self.assertEmailSent()
    """
    def setUp(self):
        """
        This method is called at the start of each test case.
        
        If you need to use this method for your own test set up, make sure
        that you call ``super()``. If not, the mail hook will not get configured
        correctly and the mail assertions will fail when they shouldn't.
        
        Here is an example of how to properly override the ``setUp`` method::
        
            import unittest
            
            from gaetestbed import MailTestCase
            
            class MyTestCase(MailTestCase, unittest.TestCase):
                def setUp(self):
                    super(MyTestCase, self).setUp()
                    # Do anything else you need here
        """
        super(MailTestCase, self).setUp()
        self._set_mail_stub()
        self.clear_sent_messages()
    
    def _set_mail_stub(self):
        """
        Updates the mail stub with a hook that intercepts messages as they're being
        logged.
        
        This grabs the mail stub from the App Engine API proxy and overwrites the
        ``_GenerateLog`` method. It simply grabs the message that would've been logged
        as sent, and adds it to the list of sent messages. You can retrieve the sent
        messages that are intercepted with the ``get_sent_messages`` helper method.
        """
        test_case = self
        class MailStub(mail_stub.MailServiceStub):
            def _GenerateLog(self, method, message, log, *args, **kwargs):
                test_case._sent_messages.append(message)
                return super(MailStub, self)._GenerateLog(method, message, log, *args, **kwargs)
        
        if 'mail' in apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map:
            del apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map['mail']
        
        apiproxy_stub_map.apiproxy.RegisterStub('mail', MailStub())
    
    def clear_sent_messages(self):
        """
        Clears the list of messages sent so far in the test case.
        
        This method is called at the start of every test in order to ensure that
        each test is fully sandboxed, though you are free to call it elsewhere in
        your tests::
        
            import unittest
        
            from gaetestbed import MailTestCase
            
            from google.appengine.api import mail
            
            class MyTestCase(MailTestCase, unittest.TestCase):
                def test_email_sent(self):
                    mail.EmailMessage(
                        to = 'test@example.org',
                        subject = 'Test E-mail',
                        sender = 'me@example.org',
                        body = 'This is a test e-mail',
                    ).send()
                    
                    # assertLength is defined in the BaseTestCase
                    self.assertLength(self.get_sent_messages(), 1)
                    
                    # Clear the sent messages
                    self.clear_sent_messages()
                    
                    # Check that the list is cleared
                    self.assertLength(self.get_sent_messages(), 0)
        """
        self._sent_messages = []
    
    def get_sent_messages(self, to=None, sender=None, subject=None, body=None, html=None):
        """
        Returns a list of ``mail.EmailMessage`` that would've been sent via App
        Engine's Mail API.
        
        As part of the sandboxing of this test case, any messages are stored only
        on a per-test basis. That is, the following assert at the start of each 
        test should always pass::
        
            self.assertEqual(self.get_sent_messages(), [])
        
        This gives you back a list of messages that would've been sent inside your
        test. Each item is a ``mail.EmailMessage`` meaning you can check the various
        fields as part of your testing::
        
            import unittest
        
            from gaetestbed import MailTestCase
            
            from google.appengine.api import mail
            
            class MyTestCase(MailTestCase, unittest.TestCase):
                def test_email_sent(self):
                    mail.EmailMessage(
                        to = 'test@example.org',
                        subject = 'Test E-mail',
                        sender = 'me@example.org',
                        body = 'This is a test e-mail',
                    ).send()
                    
                    # assertLength is defined in the BaseTestCase
                    self.assertLength(self.get_sent_messages(), 1)
                    
                    # Grab a particular message
                    message = self.get_sent_messages()[0]
                    
                    # Check that the to field is set appropriately
                    self.assertEqual(message.to, 'test@example.org')
        
        You can also use the same arguments available for ``assertEmailSent()`` in order
        to filter the messages returned. That is, if you specify a ``to`` parameter, the
        only messages returned would be those that match that recipient::
        
            import unittest
            
            from gaetestbed import MailTestCase
            
            from google.appengine.api import mail
            
            class MyTestCase(MailTestCase, unittest.TestCase): 
                def test_get_emails(self):
                    mail.EmailMessage(
                        to = 'test@example.org',
                        subject = 'Test E-mail',
                        sender = 'me@example.org',
                        body = 'This is a test e-mail',
                    ).send()
                    
                    # Check that without any parameters, all the messages are returned unfiltered
                    self.assertLength(self.get_sent_messages(), 1)
                    
                    # Since the to address is different, this will return no messages
                    self.assertLength(self.get_sent_messages(to='other@example.org'), 0)
        
        As with the ``assertEmailSent()`` method, all the filters are anded together such that any
        message returned will match *ALL* of the parameters, not just a subset.
        """
        messages = self._sent_messages
        
        if to:
            messages = [m for m in messages if to in m.to_list()]
        
        if sender:
            messages = [m for m in messages if sender == m.sender()]
        
        if subject:
            messages = [m for m in messages if subject == m.subject()]
        
        if body:
            messages = [m for m in messages if body in m.textbody()]
        
        if html:
            messages = [m for m in messages if html in m.htmlbody()]
        
        return messages
    
    def assertEmailSent(self, to=None, sender=None, subject=None, body=None, html=None):
        """
        Asserts that an e-mail with various details would be sent by App Engine.
        
        With all parameters blank, this method will fail only if the sent messages
        list is completely empty. That is, without any parameters, this only asserts
        that some Email message was somehow sent via the Mail API.
        
        If any parameters are provided, they are *anded* together such that all the
        requirements must be met by a particular message in order for the assertion to 
        pass. That is, if you specify both a recipient (``to``) and a sender (``sender``),
        a single message must match those requirements. If you send one message with
        the correct recipient and a different sender, and another with the correct sender
        and incorrect recipient, this assertion will fail.
        
        For example, the following assertion would fail::
        
            import unittest
        
            from gaetestbed import MailTestCase
            
            from google.appengine.api import mail
            
            class MyTestCase(MailTestCase, unittest.TestCase):
                def test_email_sent(self):
                    mail.send_mail(
                        to      = 'correct_recipient@example.org',
                        sender  = 'wrong_sender@example.org',
                        subject = 'Test E-mail',
                        body    = 'This is a test e-mail',
                    )
                    
                    mail.send_mail(
                        to      = 'wrong_recipient@example.org',
                        sender  = 'correct_sender@example.org',
                        subject = 'Test E-mail',
                        body    = 'This is a test e-mail',
                    )
                    
                    # This will FAIL
                    self.assertEmailSent(
                        to     = 'correct_recipient@example.org',
                        sender = 'correct_sender@example.org',
                    )
        
        All of the fields are an exact match *except* the ``body`` and ``html``
        fields where the check is whether or not the body *contains* the body specified::
        
            import unittest
        
            from gaetestbed import MailTestCase
            
            from google.appengine.api import mail
            
            class MyTestCase(MailTestCase, unittest.TestCase):
                def test_email_sent(self):
                    mail.send_mail(
                        to      = 'receiver@example.org',
                        sender  = 'sender@example.org',
                        subject = 'Test E-mail',
                        body    = 'This is a test e-mail',
                    )
                    
                    self.assertEmailSent(to='receiver@example.org')
                    self.assertEmailSent(sender='sender@example.org')
                    self.assertEmailSent(subject='Test E-mail')
                    
                    # This will pass because the body contains the string 'test'
                    self.assertEmailSent(body='test')
        """
        messages = self.get_sent_messages(
            to = to,
            sender = sender,
            subject = subject,
            body = body,
            html = html,
        )
        
        if not messages:
            failure_message = "Expected e-mail message sent."
            
            details = self._get_email_detail_string(to, sender, subject, body, html)
            if details:
                failure_message += ' Arguments expected: %s' % details
            
            self.fail(failure_message)
    
    def assertEmailNotSent(self, to=None, sender=None, subject=None, body=None, html=None):
        """
        Asserts that an e-mail with various details was not sent.
        
        With all parameters blank, this method will fail if any messages were sent. This
        is roughly equivalent to::
        
            self.assertLength(self.get_sent_messages(), 0)
        
        In short, this method behaves as exactly the opposite of ``self.assertEmailSent()``.
        Any place that assertion would pass, this should fail.
        """
        messages = self.get_sent_messages(
            to = to,
            sender = sender,
            subject = subject,
            body = body,
            html = html,
        )
        
        if messages:
            failure_message = "Unexpected e-mail message sent."
            
            details = self._get_email_detail_string(to, sender, subject, body, html)
            if details:
                failure_message += ' Arguments expected: %s' % details
            
            self.fail(failure_message)
    
    def _get_email_detail_string(self, to=None, sender=None, subject=None, body=None, html=None):
        args = []
        if to: args.append('To: %s' % to)
        if sender: args.append('From: %s' % sender)
        if subject: args.append('Subject: %s' % subject)
        if body: args.append('Body (contains): %s' % body)
        if html: args.append('HTML Body (contains): %s' % html)
        
        if args:
            return ', '.join(args)

