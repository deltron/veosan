# -*- coding: utf-8 -*-
import unittest
from base import BaseTest

class TermsTest(BaseTest):
        def test_terms_no_login(self):
            ''' Check the default terms page (nobody logged in / patient) '''

            response = self.testapp.get('/terms')
            response.mustcontain("Conditions d'utilisation")

            ''' TODO check some stuff, make sure menu isn't there '''
        
            
        def test_terms_provider_logged_in(self):
            ''' Check the terms page for a provider that has accepted them '''

            self.create_complete_provider_profile()
            self.login_as_provider()

            response = self.testapp.get('/terms')
            
            # shows this page by default
            response.mustcontain("Conditions d'utilisation")

            # check tabs/menu is present
            response.mustcontain("Provider Terms")

if __name__ == "__main__":
    unittest.main()
    
    
