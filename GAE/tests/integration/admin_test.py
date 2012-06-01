# -*- coding: utf-8 -*-
import unittest
from base import BaseTest

class AdminTest(BaseTest):
   
    def test_fill_new_provider_address_correctly(self):
        ''' fill out the new provider's address '''
        
        # init a provider
        self._test_admin_provider_init()
        self._test_fill_new_provider_address_correctly_action()
        
    def test_fill_new_provider_profile_correctly(self):
        ''' fill out the new provider's profile '''
        
        # init a provider
        self._test_admin_provider_init()
        self._test_fill_new_provider_profile_correctly_action()

    def test_fill_new_provider_address_then_modify(self):
        ''' fill out the new provider's address then modify it '''
        
        # init a provider
        self._test_admin_provider_init()
        self._test_fill_new_provider_address_correctly_action()
        self._test_modify_provider_address_action()

        
    def test_provider_schedule_set_one_timeslot(self):
        ''' Enable bookings in one timeslot '''
        
        # init a provider
        self._test_admin_provider_init()
        self._test_provider_schedule_set_one_timeslot_action()
        
        
    def test_complete_profile_creation(self):
        self.create_complete_provider_profile()
        
             
        
    def test_admin_provider_init_with_empty_email(self):
        ''' initialize a new provider with no email address (should not be possible) '''
        
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




if __name__ == "__main__":
    unittest.main()
    
    
