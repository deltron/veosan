import unittest
from google.appengine.ext import db as gdb
from google.appengine.ext import testbed
import db

class DemoTestCase(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testStoreBooking(self):
        values = { 'bookingCategory': 'physiotherapy',
                   'bookingRegion': 'mtl-downtown' 
                 }
        key = db.storeBooking(values)
        print key
        
