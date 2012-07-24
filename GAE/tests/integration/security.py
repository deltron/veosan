# -*- coding: utf-8 -*-

import logging, sys
from base import BaseTest
from datetime import datetime, timedelta
import unittest
import util, testutil
from data import db

class SecurityTest(BaseTest):
    def test_cross_access_vanity_url(self): 
        # create first provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.fill_new_provider_profile_correctly_action(as_admin = False)
        self.logout_provider()
        
        # create second provider
        self.self_signup_provider('bob@smith.com', 'bobsmith')
        
        # now try to access the first profile logged in as the second
        response = self.testapp.get('/provider/profile/%s' % self._TEST_PROVIDER_VANITY_URL)
        cross_post_response = response.follow()
        
        # cross post, you should be redirected to the login page
        cross_post_response.mustcontain("Connexion à Veosan")
    
    
    def test_form_filters_email_address(self): 
        # create first provider
        response = self.testapp.post('/signup')
        
        signup_form = response.forms['signup_form']
        signup_form['email'] = 'miXed@CaSe.CoM'
        
        password_response = signup_form.submit()
        
        password_response.mustcontain(no='miXed@CaSe.CoM')
        password_response.mustcontain('mixed@case.com')
        
            
    def test_brackets_in_bio(self): 
        # create first provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.fill_new_provider_profile_correctly_action(as_admin = False)
        
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['experience_form']
        
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = '<not allowed in here!'
        
        #experience_form['title'] = 'Manual Physiotherapy'
        #experience_form['description'] = "<not allowed in here!"

        response2 = experience_form.submit()
        
        response2.showbrowser()
        response2.mustcontain('(not allowed in here!')
        response2.mustcontain(no='<not allowed in here!')
