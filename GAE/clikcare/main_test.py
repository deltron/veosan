'''
Created on Wednesday
@author: phil
'''
import unittest
import db
import logging
import webapp2
import main

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testProviderAddressHandlerPOST(self):
        # create fake request
        request = webapp2.Request.blank('/provider/address')
        request.method = 'GET'
        # Get a response for that request.
        response = request.get_response(main.application)
        #patient_key = db.storePatient(request)
        self.assertEqual(response.status_int, 500)
            
        
if __name__ == "__main__":
    unittest.main()