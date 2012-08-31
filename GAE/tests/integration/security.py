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
        self.self_signup_provider()
        self.fill_new_provider_profile_correctly_action(as_admin = False)
        self.logout_provider()
        
        # create second provider
        self.self_signup_provider('bob@smith.com', 'bobsmith')
        
        # now try to access the first profile logged in as the second
        response = self.testapp.get('/provider/profile/%s' % self._TEST_PROVIDER_VANITY_URL)
        cross_post_response = response.follow()
        
        # cross post, you will be redirected to public profile of person you are trying to access
        cross_post_response.mustcontain("schema.org/Person")
        cross_post_response.mustcontain("first")
        cross_post_response.mustcontain("last")

    
    def test_form_filters_email_address(self): 
        # create first provider
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['email'] = 'miXed@CaSe.CoM'
        
        password_response = signup_form.submit()
        
        password_response.mustcontain(no='miXed@CaSe.CoM')
        password_response.mustcontain('mixed@case.com')
        
            
    def test_brackets_in_bio(self): 
        # create first provider
        self.self_signup_provider()
        self.fill_new_provider_profile_correctly_action(as_admin = False)
        
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['experience_form']
        
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = 'Manual Physiotherapy'
        experience_form['description'] = "<not allowed in here!"

        response2 = experience_form.submit().follow()
        
        response2.mustcontain('&lt;not allowed in here!')
        response2.mustcontain(no='<not allowed in here!')


    def test_referer_length(self): 
        really_long_referer = "http://googleads.g.doubleclick.net/pagead/ads?client=ca-pub-7617687509476570&output=html&h=250&slotname=2494861371&w=300&lmt=1346007695&flash=11.3.300.271&url=http%3A%2F%2Fwww.websitelooker.com%2Fwww%2Fmethodesossante.com&dt=1346007695933&bpp=4&shv=r20120815&jsv=r20110914&prev_slotnames=4490909541%2C2494861371&correlator=1346007695686&frm=20&adk=837188088&ga_vid=467908494.1346007592&ga_sid=1346007592&ga_hid=289597716&ga_fc=1&u_tz=-240&u_his=2&u_java=1&u_h=800&u_w=1280&u_ah=770&u_aw=1280&u_cd=24&u_nplug=0&u_nmime=0&dff=times%20new%20roman&dfs=16&adx=817&ady=696&biw=1263&bih=628&oid=3&ref=http%3A%2F%2Fwww.bing.com%2Fsearch%3Fq%3Dmethodesossante.com%26form%3DMSNH56%26mkt%3Dfr-ca%26qs%3DAS%26sk%3D%26pq%3Dmethodesos%26sp%3D1%26sc%3D2-10&docm=9&fu=0&ifi=3&dtd=111&xpc=GmTEh3RATq&p=http%3A//www.websitelooker.com"
        
        self.assertEqual(len(really_long_referer), 815)
        
        headers = { "Referer" : really_long_referer }
        response = self.testapp.get('/', headers=headers)
        
        response.mustcontain("Pour les professionnels de la santé")
        
        
        
    def test_access_provider_pages_not_logged_in(self): 
        self.self_signup_provider()
        self.fill_new_provider_profile_correctly_action(as_admin = False)
        self.logout_provider()
        
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL).follow()
        
        # check this is the public profile
        response.mustcontain("schema.org/Person")