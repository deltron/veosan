# -*- coding: utf-8 -*-
import datetime
import unittest
from base import BaseTest

class TermsTest(BaseTest):
        def test_terms_no_login(self):
            ''' Check the default terms page (nobody logged in / patient) '''

            response = self.testapp.get('/terms')
            response.mustcontain("Conditions d'utilisation")
            
            if "Conditions pour fournisseurs" in response:
                self.assertTrue("False", "Menu should not appear")
        
            
        def test_terms_provider_logged_in(self):
            ''' Check the terms page for a provider that has accepted them '''

            self.create_complete_provider_profile()
            self.login_as_provider()

            response = self.testapp.get('/terms')
            
            # shows this page by default
            response.mustcontain("Conditions d'utilisation")

            # check tabs/menu is present
            response.mustcontain("Conditions pour fournisseurs")
            
            # click on the provider terms link
            response = self.testapp.get('/provider/terms')
            
            # Check first name, last name
            response.mustcontain("Fantastic", "Fox")
            
            # email
            response.mustcontain(self._TEST_PROVIDER_EMAIL)

            # phone and address
            response.mustcontain("555-123-5678", "123 Main St.", "Westmount", "H1B2C3")

            # acceptance date
            response.mustcontain("Terms agreed on")
            
            today = datetime.datetime.now()
            response.mustcontain(today.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    unittest.main()
    
    
