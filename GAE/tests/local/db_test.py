
import logging
from datetime import datetime
from base_test import BaseTestCase
from data import db, db_util, db_book
from data.model import Provider, Booking, Schedule

class DBTestCase(BaseTestCase):

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
        entity = db.Provider()
        multidict = { 'onsite': 'y' }   
        db_util.set_all_properties_on_entity_from_multidict(entity, multidict)


    def testFindBestProviderForBooking(self):
        testCategory = u'physiotherapy'
        testLocation = u'montreal-west'
        
        # create provider
        p = Provider()
        p.terms_agreement=True
        p.first_name = 'Best-Test'
        p.last_name = 'Phys-Io'
        p.category = testCategory
        p.location = testLocation
        pkey = p.put()
        # add a provider's schedule (Thursday Morning)
        s = Schedule()
        s.day = 3
        s.startTime = 8
        s.endTime = 12
        s.provider = p.key
        s.put()
        # create provider with no schedule
        p = Provider()
        p.first_name = 'NoSchedule'
        p.last_name = 'Phys-Io'
        p.category = testCategory
        p.location = testLocation
        pkey2 = p.put()
        # 2 providers in db
        self.assertEqual(2, Provider.query().count(), '2 providers in datastore')
        # create booking
        b = Booking()
        b.requestCategory = testCategory
        b.requestRegion = testLocation
        b.requestDateTime = datetime.strptime('2012-04-26 10', '%Y-%m-%d %H')
        b.put();
        # test the matching
        bestProvider = db_book.findBestProviderForBookingRequest(b)
        logging.info('best provider:' + str(bestProvider))
        # assert
        self.assertIsNotNone(bestProvider, 'provider should not be None')
        self.assertEqual(pkey, bestProvider.key, 'provider keys should be equal')
        
        
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
        bestProvider = db_book.findBestProviderForBookingRequest(b)
        logging.info('best provider:' + str(bestProvider))
        # assert
        self.assertEqual(None, bestProvider, 'provider keys should be None')