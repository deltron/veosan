# -*- coding: utf-8 -*-

import logging, sys
from base import BaseTest
from datetime import datetime, timedelta
import unittest
import util, testutil
from data import db

class SignupTest(BaseTest):
    
    def test_signup(self):
        ''' Test signup as anonymous user '''
        response = self.testapp.get("/login")
        
        signup_form = response.forms[1] # signup form
        signup_form['provider_email'] = 'test_signup@tester.com'
        signup_form['provider_postalcode'] = 'H1H2C2'
        
        response = signup_form.submit()
        
        # will be redirected to main page
        response = response.follow()
        response.mustcontain("Trouvez des soins")
        
        # now check we received the signup email
        messages = self.mail_stub.get_sent_messages(to='cliktester@gmail.com')
        self.assertEqual(1, len(messages))
        m = messages[0]    
            
        self.assertEqual(m.subject, 'Request for signup from provider')
        self.assertEqual(m.sender, 'cliktester@gmail.com')
        self.assertEqual(m.body.payload, 'Received sign-up request from email->test_signup@tester.com postal_code->H1H2C2')

        
        
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    unittest.main()
    
    
