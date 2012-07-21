
import logging
from data.test_data import create_test_providers
from base_test import BaseTestCase
from data.model import Provider, Booking
from data import db_search
from utilities.time import Timeslot, create_one_hour_timeslot
from datetime import date, datetime
import util
import testutil

class BookingTestCase(BaseTestCase):
    
    def test_timeslot_equality(self):
        dt1 = datetime(2012, 04, 17, 4, 34)
        dt2 = datetime(2012, 04, 17, 4, 34)
        ts1 = create_one_hour_timeslot(dt1)
        ts2 = create_one_hour_timeslot(dt2)
        self.assertEqual(ts1, ts2) 
    
    def test_print_timeslot(self):
        ts = Timeslot(datetime.now(), datetime.now())
        s = 'timeslot %s %s' % ts
        logging.info(s)
     
    def test_create_timeslots_over_range(self):
        ts = db_search.create_one_hour_timeslots_over_range(date.today(), 8, 12)
        logging.info(ts)
        self.assertEquals(4, len(ts))
        
    def test_find_providers_perfect_and_imperfect(self):
        providers = create_test_providers()
        logging.info("providers: %s" % providers)
        self.assertEqual(len(providers), Provider.query().count())
        # create booking request
        next_monday_at_9 = testutil.create_datetime_from_weekday_and_hour(5, 15)
        booking_request = Booking(request_category=util.CAT_PHYSIO, request_location='mtl-downtown', request_datetime=next_monday_at_9)
        booking_responses = db_search.provider_search(booking_request)
        logging.info('Booking Respones:')
        for br in booking_responses:
            logging.info('providers %s on %s at %s' % (br.provider.full_name(), br.timeslot.start.date(), br.timeslot.start.time()))
        # 2 responses
        self.assertEqual(2, len(booking_responses))
        # first provider is perfet match
        br1 = booking_responses[0]
        self.assertTrue(br1.is_perfect_match(booking_request))
        # second provider is not perfect match
        br2 = booking_responses[1]
        self.assertFalse(br2.is_perfect_match(booking_request))
        # assert top provider is p2
        self.assertEqual(providers[1][0], booking_responses[0].provider.key)
        
    def test_find_providers_all_imperfect_matches(self):
        providers = create_test_providers()
        # create booking request - Saturday at 10 PM
        sat_at_10 = testutil.create_datetime_from_weekday_and_hour(5, 22)
        booking_request = Booking(request_category=util.CAT_PHYSIO, request_location='mtl-downtown', request_datetime=sat_at_10)
        booking_responses = db_search.provider_search(booking_request)
        logging.info('Booking Respones:')
        for br in booking_responses:
            logging.info('providers %s on %s at %s' % (br.provider.full_name(), br.timeslot.start.date(), br.timeslot.start.time()))
        for br in booking_responses:
            self.assertFalse(br.is_perfect_match(booking_request))
        # assert top provider is p2
        self.assertEqual(providers[1][0], booking_responses[0].provider.key)
        
    def test_find_providers_no_matches_wrong_category(self):
        providers = create_test_providers()
        # create booking request - Saturday at 10 PM
        sat_at_10 = testutil.create_datetime_from_weekday_and_hour(5, 22)
        booking_request = Booking(request_category='osteopath', request_location='mtl-downtown', request_datetime=sat_at_10)
        booking_responses = db_search.provider_search(booking_request)
        logging.info('Booking Respones:')
        # assert top provider is p2
        self.assertEqual(0, len(booking_responses))
        
        
        