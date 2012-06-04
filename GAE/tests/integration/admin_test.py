# -*- coding: utf-8 -*-
import unittest
from base import BaseTest
from data import db

class AdminTest(BaseTest):
   
    def test_fill_new_provider_address_correctly(self):
        ''' fill out the new provider's address '''
        
        # init a provider
        self.login_as_admin()
        self.init_new_provider()
        self.fill_new_provider_address_correctly_action()
        
    def test_fill_new_provider_profile_correctly(self):
        ''' fill out the new provider's profile '''
        
        # init a provider
        self.login_as_admin()
        self.init_new_provider()
        self._test_fill_new_provider_profile_correctly_action()

    def test_fill_new_provider_address_then_modify(self):
        ''' fill out the new provider's address then modify it '''
        
        # init a provider
        self.login_as_admin()
        self.init_new_provider()
        self.fill_new_provider_address_correctly_action()
        self.modify_provider_address_action()

        
    def test_provider_schedule_set_one_timeslot(self):
        ''' Enable bookings in one timeslot '''
        
        # init a provider
        self.login_as_admin()
        self.init_new_provider()
        self.provider_schedule_set_one_timeslot_action()
        
        
    def test_complete_profile_creation(self):
        self.login_as_admin()
        self.create_complete_provider_profile()
        
        
    def test_admin_provider_init_with_empty_email(self):
        ''' initialize a new provider with no email address (should not be possible) '''
        
        self.login_as_admin()
                
        request_variables = { 'provider_email' : '' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        
        # this should fail with an error message
        
        # check for error message
        response.mustcontain("Addresse courriel invalide.")
        
        # if anything below here is in the response, it's not good!
    
        # Check signs of success
        if "Initialized new provider for " in response:
            self.assertTrue(False, "A provider was created without an email address")


    def test_admin_provider_init_with_invalid_email(self):
        ''' initialize a new provider with invalid address (should not be possible) '''
        
        self.login_as_admin()

        request_variables = { 'provider_email' : 'aaabbbccc' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        
        # this should fail with an error message
        
        # check for error message
        response.mustcontain("Addresse courriel invalide.")
        
        # if anything below here is in the response, it's not good!
    
        # Check signs of success
        if "Initialized new provider for " in response:
            self.assertTrue(False, "A provider was created without an email address")
            
    def test_new_provider_solicit_with_empty_profile(self):
        # set things up
        self.login_as_admin()
        self.init_new_provider()

        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/administration', request_variables)

        response.mustcontain('Provider Administration')
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        solicit_form = response.forms[0]
        # sends an email to the provider
        response = solicit_form.submit()
        
        # check error message is displayed
        response.mustcontain("Incomplete profile")

        # make sure no email is sent
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(0, len(messages))


if __name__ == "__main__":
    unittest.main()
    
    
