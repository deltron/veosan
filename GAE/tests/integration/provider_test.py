# -*- coding: utf-8 -*-

import unittest, webtest
from google.appengine.ext import testbed
import main, db
from admin_test import AdminTest

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

    def test_enable_all_time_slots(self):
        pass
        
        

if __name__ == "__main__":
    unittest.main()
    
    
