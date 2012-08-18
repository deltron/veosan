# -*- coding: utf-8 -*-

import logging, sys
from base import BaseTest
from datetime import datetime, timedelta
import unittest
import util, testutil
from data import db

class SignupTest(BaseTest):
    def test_teaser(self):
        ''' Test signup as anonymous patient '''
        
        util.BOOKING_ENABLED = False
        
        response = self.testapp.get("/signup/patient")
        
        signup_form = response.forms[0] # signup form
        signup_form['first_name'] = 'patrick'
        signup_form['last_name'] = 'patient'
        signup_form['email'] = 'test_signup@tester.com'
        signup_form['postal_code'] = 'H1H2C2'
        
        response = signup_form.submit()
        
        response.mustcontain("Merci pour votre intérêt. Nous serons en contact bientôt!")
        
        # now check if it's in the database
        self.login_as_admin()
        response = self.testapp.get("/admin/patients")

        response.mustcontain("patrick")
        response.mustcontain("patient")
        response.mustcontain("test_signup@tester.com")
        response.mustcontain("H1H2C2")

    
    def test_signup(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        signup_form['postal_code'] = 'h1h1h1'
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
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        signup_form['postal_code'] = 'h1h 1h1'
        response = signup_form.submit()

        #hidden field contains postal code
        response.mustcontain('H1H1H1')

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")


    def test_signup_vanity_name_collision(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        signup_form['postal_code'] = 'h1h1h1'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
        self.logout_provider()
        
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = 'another_email@server.com'
        signup_form['postal_code'] = 'h1h1h1'
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
        
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = 'yet_another_email@server.com'
        signup_form['postal_code'] = 'h1h1h1'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
        provider = db.get_provider_from_email('yet_another_email@server.com')
        self.assertEqual(provider.vanity_url, 'firstlast2')
        

    def test_signup_vanity_name_space_last_name(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last another'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        signup_form['postal_code'] = 'h1h1h1'
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
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'Renée'
        signup_form['last_name'] = 'St-Vil'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        signup_form['postal_code'] = 'H4Z 2P9'
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
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'Renée'
        signup_form['last_name'] = 'St-Vilàîèöêûç'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        signup_form['postal_code'] = 'H4Z 2P9'
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


    def test_signup_back_button(self):
        ''' Basic signup process for a new provider '''
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = self._TEST_PROVIDER_EMAIL
        signup_form['postal_code'] = 'h1h1h1'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")

        # now do it again (simulates hitting reload or back button)
        response = self.testapp.post('/signup/provider2')
        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['first_name'] = 'first'
        signup_form2['last_name'] = 'last'
        signup_form2['email'] = self._TEST_PROVIDER_EMAIL
        signup_form2['postal_code'] = 'h1h1h1'
        
        profile_response = signup_form2.submit()
        profile_response.mustcontain("Bienvenue")
        
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    unittest.main()
    
    
