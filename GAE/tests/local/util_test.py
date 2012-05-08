'''
Created on Wednesday
@author: phil
'''
import unittest
import util
import logging

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testGetDatesList(self):
        dates = util.getDatesList()
        print(dates)
        self.assertEqual( len(dates), 21)

        
if __name__ == "__main__":
    unittest.main()