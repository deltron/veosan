'''
Created on Wednesday
@author: phil
'''
import unittest
import db
import sys
import logging
import webapp2
import main
from google.appengine.ext import testbed

class MainTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testProviderAddressHandlerPOST(self):
        # create fake request
        request = webapp2.Request.blank('/admin/provider/address')
        request.method = 'GET'
        # Get a response for that request.
        response = request.get_response(main.application)
        #patient_key = db.storePatient(request)
        self.assertEqual(response.status_int, 500)

        
if __name__ == "__main__":
    unittest.main()