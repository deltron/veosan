# -*- coding: utf-8 -*-

import unittest, webtest
from google.appengine.ext import testbed
import main, db

class AdminTest(unittest.TestCase):
    ''' *** NOTE ***
    
    Settings in app.yaml are ignored by tests
    App assumes login is "magically" handled properly
    
    '''

    def setUp(self):
        # Wrap the app with WebTest’s TestApp.
        self.testapp = webtest.TestApp(main.application)
        
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_blobstore_stub()
        
    def tearDown(self):
        self.testbed.deactivate()

    def test_admin_provider_init(self):
        ''' initialize a new provider '''
        
        request_variables = { 'providerEmail' : 'unit_test@provider.com' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        response.mustcontain("Initialized new provider for unit_test@provider.com")
        response.mustcontain("None, None [unit_test@provider.com]")
        

    def test_fill_new_provider_profile_correctly(self):
        ''' fill out the new provider's profile '''
        
        # init a provider
        self.test_admin_provider_init()
        
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key() }
        response = self.testapp.get('/provider/address', request_variables)
        
        address_form = response.forms[0] # address form
        
        # check email address is pre-populated
        self.assertEqual(address_form['email'].value, "unit_test@provider.com")

        # fill out the form
        address_form['prefix'] = "Mr."
        address_form['firstName'] = "Fantastic"
        address_form['lastName'] = "Fox"
        address_form['postfix'] = "Ph.D"
        address_form['phone'] = "555-123-5678"
        address_form['region'] = "mtl-downtown"
        address_form['address'] = "123 Main St."
        address_form['city'] = "Westmount"
        address_form['postalCode'] = "H1B2C3"
        
        # submit it
        address_form.submit()
        
        # check values in database
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # iterate over every field item, find the match in the provider object and check its equality
        # possible we miss something here?
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # go back to the admin page, check the name is updated
        response = self.testapp.get('/admin/providers')
        response.mustcontain("Fox, Fantastic [unit_test@provider.com]")


    def test_upload_image_to_correct_profile(self):
        ''' Upload a test image for the new provider '''
        
        self.test_fill_new_provider_profile_correctly()
        
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key() }
        response = self.testapp.get('/provider/address', request_variables)
        
        photo_form = response.forms[1] # photo form
        
        print photo_form.fields.values()
        
        photo_form['profilePhoto'] = ('profilePhoto', 'provider-test-image.png')
        
        photo_form.submit()
        
        # hmm can't upload
        
        

if __name__ == "__main__":
    unittest.main()
    
    
