# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db 

class ProviderTest(BaseTest):

    def test_administration_tab_not_visible_to_provider(self):
        # setup a provider
        self.create_complete_provider_profile()
        self.logout_provider()
        # login as provider
        self.login_as_provider()
        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/address', request_variables)
        # patient name in navbar
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain('Adresse')
        response.mustcontain('Fantastic')
        response.mustcontain('Fox')
        assert 'Administration' not in response 

if __name__ == "__main__":
    unittest.main()
    
    
