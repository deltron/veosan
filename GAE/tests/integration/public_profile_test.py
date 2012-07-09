# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class PublicProfileTest(BaseTest):
    
    def test_visit_public_profile(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        
    def test_create_vanity_url_existing_address(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        
        # now create another provider with bobafett
        
        self.login_as_admin()
        
        # init a provider
        self.init_new_provider(provider_email="bobafett@veosan.com")

        # fill all sections

        # get the provider key
        provider = db.get_provider_from_email("bobafett@veosan.com")
        
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/admin/provider/address', request_variables)
        
        address_form = response.forms[0] # address form
        
        # fill out the form
        address_form['title'] = u"Mr."
        address_form['first_name'] = u"Fred"
        address_form['last_name'] = u"Fox"
        address_form['credentials'] = u"Ph.D"
        address_form['phone'] = u"555-123-5678"
        address_form['location'] = u"mtl-downtown"
        address_form['address'] = u"123 Main St."
        address_form['city'] = u"Westmount"
        address_form['postal_code'] = u"H1B2C3"
        address_form['vanity_url'] = self._TEST_PROVIDER_VANITY_URL

        
        # submit it
        response = address_form.submit()
        response.mustcontain("That name is already taken, please choose another one.")

        # make sure profile for that Vanity URL still points to the old provider
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")


    

if __name__ == "__main__":
    unittest.main()
    
    
