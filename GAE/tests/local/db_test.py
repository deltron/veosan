
import logging
from datetime import datetime
from base_test import BaseTestCase
from data import db, db_search
from data.model import Provider, Booking, Schedule
from webob import MultiDict

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


    def test_set_property_on_entity_from_multidict(self):
        entity = db.Provider()
        multidict = MultiDict({ 'last_name': 'lntest' })
        #db_util.set_all_properties_on_entity_from_multidict(entity, multidict)
        self.assertEquals(entity.last_name, 'lntest')

    def testFindBestProviderForBooking(self):
        testCategory = u'physiotherapy'
        testLocation = u'montreal-west'
        
        # create provider
        p = Provider()
        p.terms_agreement=True
        p.status = 'client_enabled'
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
        b.request_category = testCategory
        b.request_location = testLocation
        b.request_datetime = datetime.strptime('2012-04-26 10', '%Y-%m-%d %H')
        b.put();
        # test the matching
        brs = db_search.provider_search(b)
        logging.info('best provider:' + str(brs))
        # assert
        self.assertIsNotNone(brs, 'provider should not be None')
        self.assertEqual(pkey, brs[0].provider.key, 'provider keys should be equal')
        