# -*- coding: utf-8 -*-

import unittest, webtest
from google.appengine.ext import testbed
from google.appengine.api import users
import main

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
        
    def tearDown(self):
        self.testbed.deactivate()

    def test_admin_provider_init(self):
        ''' initialize a new provider '''
        
        vars = { 'providerEmail' : 'unit_test@provider.com' }
        
        response = self.testapp.post('/admin/provider/init', vars)
        
        print response.body

        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "Abc")
        


if __name__ == "__main__":
    unittest.main()
    
    
