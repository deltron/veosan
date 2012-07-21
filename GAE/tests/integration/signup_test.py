# -*- coding: utf-8 -*-

import logging, sys
from base import BaseTest
from datetime import datetime, timedelta
import unittest
import util, testutil
from data import db

class SignupTest(BaseTest):
    def test_teaser(self):
        ''' Test signup as anonymous user '''
        
        util.BOOKING_ENABLED = False
        
        response = self.testapp.get("/")
        
        signup_form = response.forms[0] # signup form
        signup_form['role'] = 'patient'
        signup_form['from_email'] = 'test_signup@tester.com'
        signup_form['postal_code'] = 'H1H2C2'
        
        response = signup_form.submit()
        
        response.mustcontain("Merci pour votre intérêt. Nous serons en contact bientôt!")
        
        # now check we received the signup email
        messages = self.mail_stub.get_sent_messages(to='support@veosan.com')
        self.assertEqual(1, len(messages))
        m = messages[0]    
            
        self.assertEqual(m.subject, 'Request for signup : %s' % 'test_signup@tester.com')
        self.assertEqual(m.sender, 'support@veosan.com')
        self.assertIn('H1H2C2', m.body.payload)
        self.assertIn('patient', m.body.payload)

        
    
    
    def test_signup(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.get("/signup")
        
        signup_form = response.forms['signup_form'] 
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        signup_form['vanity_url'] = self._TEST_PROVIDER_VANITY_URL
        password_choice_response = signup_form.submit()
        password_choice_response = password_choice_response.follow()
        
        password_choice_response.mustcontain('Choisissez votre mot de passe')
        password_form = password_choice_response.forms[0]
        password_form['password'] = self._TEST_PROVIDER_PASSWORD
        password_form['password_confirm'] = self._TEST_PROVIDER_PASSWORD

        welcome_response = password_form.submit()
        welcome_response = welcome_response.follow()
        self.assertEqual(welcome_response.status_int, 200)
        welcome_response.mustcontain(u'Bienvenue chez Veosan!')

        
        
        
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    unittest.main()
    
    
