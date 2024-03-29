# -*- coding: utf-8 -*-

import logging, sys
from base import BaseTest
from datetime import datetime, timedelta
import unittest
import util, testutil
from data import db

class SignupTest(BaseTest):

    
    def test_signup(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")

    def test_signup_space_in_postal_code(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")


    def test_signup_vanity_name_collision(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
        self.logout_provider()
        
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = 'another_email@server.com'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
        provider = db.get_provider_from_email('another_email@server.com')
        self.assertEqual(provider.vanity_url, 'firstlast1')
        
        self.logout_provider()
        
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = 'yet_another_email@server.com'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
        provider = db.get_provider_from_email('yet_another_email@server.com')
        self.assertEqual(provider.vanity_url, 'firstlast2')
        

    def test_signup_vanity_name_space_last_name(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last another'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEqual(provider.vanity_url, 'firstlastanother')
                

    def test_signup_vanity_name_accent(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'Renée'
        signup_form['last_name'] = 'St-Vil'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEqual(provider.vanity_url, 'reneestvil')
                
    def test_signup_vanity_name_every_accent(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'Renée'
        signup_form['last_name'] = 'St-Vilàîèöêûç'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEqual(provider.vanity_url, 'reneestvilaieoeuc')

    def test_signup_partial_provider(self):
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()
        
        partial_provider = db.get_partial_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEqual(partial_provider.first_name, 'first')
        self.assertEqual(partial_provider.last_name, 'last')
        self.assertEqual(partial_provider.email, self._TEST_PROVIDER_EMAIL)


    def test_signup_partial_provider_multiple_times(self):
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()
        
        partial_provider = db.get_partial_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEqual(partial_provider.first_name, 'first')
        self.assertEqual(partial_provider.last_name, 'last')
        self.assertEqual(partial_provider.email, self._TEST_PROVIDER_EMAIL)

        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last2'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()
        
        partial_provider = db.get_partial_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEqual(partial_provider.first_name, 'first')
        self.assertEqual(partial_provider.last_name, 'last')
        self.assertEqual(partial_provider.email, self._TEST_PROVIDER_EMAIL)

        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()
        
        partial_provider = db.get_partial_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEqual(partial_provider.first_name, 'first')
        self.assertEqual(partial_provider.last_name, 'last')
        self.assertEqual(partial_provider.email, self._TEST_PROVIDER_EMAIL)

    def test_signup_partial_provider_completed(self):
        response = self.testapp.post('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        response = signup_form.submit()
        
        partial_provider = db.get_partial_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEqual(partial_provider.first_name, 'first')
        self.assertEqual(partial_provider.last_name, 'last')
        self.assertEqual(partial_provider.email, self._TEST_PROVIDER_EMAIL)

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'
        
        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")

        partial_provider = db.get_partial_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertIsNone(partial_provider)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    unittest.main()
    
    
