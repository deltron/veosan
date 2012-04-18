import unittest
from google.appengine.ext import db as gdb
from google.appengine.ext import testbed
import db
import logging, sys
from data import Provider, Booking

class DBTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.info("TEST LOGGING")
        print('setup')
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        print('tearDown')
        self.testbed.deactivate()

    def testStoreBooking(self):
        values = { 'bookingCategory': 'physiotherapy',
                   'bookingRegion': 'mtl-downtown' 
                 }
        key = db.storeBooking(values, None, None)
        print key
        
    def testFindBestProviderForBooking(self):
        testCategory = u'physiotherapy'
        # create provider
        p = Provider()
        p.firstName = 'Best-Test'
        p.lastName = 'Phys-Io'
        p.category = testCategory
        pkey = p.put()
        # create booking
        b = Booking()
        b.requestCategory = testCategory
        b.put();
        # test the matching
        bestProvider = db.findBestProviderForBooking(b)
        logging.info('best provider:' + str(bestProvider))
        # assert
        self.assertEqual(pkey, bestProvider.key(), 'provider keys should be equal')