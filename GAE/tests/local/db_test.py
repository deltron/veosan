
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

    def test_schedule_no_merge(self):
        s1 = Schedule(day='monday', start_time=9, end_time=13)
        s1.put()
        s2 = Schedule(day='monday', start_time=14, end_time=18)
        s2.put()
        # check that there was no merge
        self.assertEquals(s2.start_time, 14)
        self.assertEquals(s2.end_time, 18)
      
    def test_schedule_simple_merge(self):
        s1 = Schedule(day='monday', start_time=9, end_time=15)
        s1.put()
        s2 = Schedule(day='monday', start_time=13, end_time=18)
        s2.put()
        # check that merge was done
        self.assertEquals(s2.start_time, 9)
        self.assertEquals(s2.end_time, 18)

    def test_schedule_double_merge(self):
        s1 = Schedule(day='monday', start_time=8, end_time=11)
        s1.put()
        s2 = Schedule(day='monday', start_time=14, end_time=18)
        s2.put()
        # check - no merge
        self.assertEquals(s2.start_time, 14)
        self.assertEquals(s2.end_time, 18)
        s3 = Schedule(day='monday', start_time=10, end_time=14)
        s3.put()
        # check that merge was done
        self.assertEquals(s3.start_time, 8)
        self.assertEquals(s3.end_time, 18)
        
        schedules = Schedule.query(Schedule.day=='monday').fetch()
        self.assertEquals(len(schedules), 1, 'Should only be one schedule stored')
        self.assertEquals(schedules[0].start_time, 8)
        self.assertEquals(schedules[0].end_time, 18)
        self.assertEquals(schedules[0].day, 'monday')
                

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
        p.vanity_url = 'physio_guy'
        pkey = p.put()
        # add a provider's schedule (Thursday Morning)
        s = Schedule()
        s.day = 'thursday'
        s.start_time = 8
        s.end_time = 12
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
        