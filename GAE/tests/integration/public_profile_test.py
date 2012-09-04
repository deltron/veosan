# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
import logging
from data import db
import testutil
from datetime import datetime
from utilities import time
from babel.dates import format_date, format_datetime, format_time

class PublicProfileTest(BaseTest):
    
    def test_visit_public_profile(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: public view")

    def test_visit_public_profile_self_view(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        self.login_as_provider()

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: self-view")

    def test_visit_public_profile_admin_view(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        self.login_as_admin()

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: public view", admin=True)


    def test_visit_public_profile_from_another_loggedin_provider(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")


        # and another
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'david'
        signup_form['last_name'] = 'mctester'
        signup_form['email'] = 'mctest@veosan.com'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'dentist'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        
        # should be on the welcome page
        profile_response.mustcontain("Bienvenue!")
        profile_response.mustcontain("Comment naviguer sur le site")

        # revist first guy's public page
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)

        # check the menu items
        public_profile.mustcontain('mctest@veosan.com')
        public_profile.mustcontain('/provider/profile/davidmctester')
        public_profile.mustcontain('/provider/address/davidmctester')
        public_profile.mustcontain('/provider/welcome/davidmctester')


    def test_disable_enable_show_address(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # hide last name
        public_profile.mustcontain("Fantastic Fox")
                
        public_profile.mustcontain(no="Map")
        public_profile.mustcontain(no="Réservez Maintenant")
        
        # enable the address
        self.login_as_admin()
        enable = self.testapp.get('/admin/provider/feature/address_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Map")
        
        
        # hit it again to disable the address
        disable = self.testapp.get('/admin/provider/feature/address_enabled/' + self._TEST_PROVIDER_VANITY_URL)

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        
    def test_disable_enable_show_booking(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        
        self.login_as_admin()
        
        public_profile.mustcontain(no="Map")

        
        # enable the booking
        enable = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Réservez Maintenant")
        
        
        # hit it again to disable the booking
        disable = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Réservez Maintenant")
        
        



if __name__ == "__main__":
    unittest.main()
    
    
