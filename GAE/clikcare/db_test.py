'''
Created on Wednesday
@author: phil
'''
import unittest
import db
import logging
import webapp2

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass
        

    def testCreateProvider(self):
        provider = db.getOrCreateProvider(None)
        print(provider)
        self.assertIsNotNone(provider, 'Provider should have been created')
        
        
if __name__ == "__main__":
    unittest.main()