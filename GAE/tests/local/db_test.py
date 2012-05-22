import unittest
from google.appengine.ext import db as gdb
from google.appengine.ext import testbed
import db, logging
from datetime import datetime
from data import Provider, Booking, Schedule

class DBTestCase(unittest.TestCase):
    def setUp(self):
        print('setup ' + self._testMethodName)
        logging.basicConfig(level=logging.DEBUG)
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        print('tearDown ' + self._testMethodName)
        self.testbed.deactivate()
        print('-------------------------------')

    def testStoreBooking(self):
        values = { 'category': 'physiotherapy',
                   'location': 'mtl-downtown', 
                   'booking_date': '2012-04-17',
                   'booking_time': '10',
                   'comments': 'no comments',
                 }
        key = db.storeBooking(values, None, None)
        print key

    def test_set_all_properties_on_entity_from_multidict_boolean(self):
        entity = db.Provider
        multidict = { 'onsite': 'y' }
        
        db.set_all_properties_on_entity_from_multidict(entity, multidict)



    def testFindBestProviderForBooking(self):
        testCategory = u'physiotherapy'
        testRegion = u'montreal-west'
        
        # create provider
        p = Provider()
        p.first_name = 'Best-Test'
        p.last_name = 'Phys-Io'
        p.category = testCategory
        p.region = testRegion
        pkey = p.put()
        # add a provider's schedule (Thursday Morning)
        s = Schedule()
        s.day = 3
        s.startTime = 8
        s.endTime = 12
        s.provider = p
        s.put()
        # create provider with no schedule
        p = Provider()
        p.first_name = 'NoSchedule'
        p.last_name = 'Phys-Io'
        p.category = testCategory
        p.region = testRegion
        pkey2 = p.put()
        
        # create booking
        b = Booking()
        b.requestCategory = testCategory
        b.requestRegion = testRegion
        b.requestDateTime = datetime.strptime('2012-04-26 10', '%Y-%m-%d %H')
        b.put();
        # test the matching
        bestProvider = db.findBestProviderForBooking(b)
        logging.info('best provider:' + str(bestProvider))
        # assert
        self.assertIsNotNone(bestProvider, 'provider should not be None')
        self.assertEqual(pkey, bestProvider.key(), 'provider keys should be equal')
        
        
    def testCantFindProvider(self):
        testCategory = u'physiotherapy'
        testRegion = u'montreal-west'
        otherRegion = u'montreal-downtown'
        # create provider
        p = Provider()
        p.first_name = 'Best-Test'
        p.last_name = 'Phys-Io'
        p.category = testCategory
        p.region = testRegion
        pkey = p.put()
        # create booking
        b = Booking()
        b.requestCategory = testCategory
        b.requestRegion = otherRegion
        b.requestDateTime = datetime.strptime('2012-04-26 10', '%Y-%m-%d %H')
        b.put();
        # test the matching
        bestProvider = db.findBestProviderForBooking(b)
        logging.info('best provider:' + str(bestProvider))
        # assert
        self.assertEqual(None, bestProvider, 'provider keys should be None')