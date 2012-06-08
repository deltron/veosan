
import logging
from test_data import create_test_providers
from base_test import BaseTestCase
from data.model import Provider, Booking
from data import db_book
import util
import testutil

class BookingTestCase(BaseTestCase):
    
    def test_find_best_provider_without_perfect_match(self):
        providers = create_test_providers()
        logging.info("providers: %s" % providers)
        self.assertEqual(len(providers), Provider.query().count())
        
        # create booking request
        next_monday_at_9 = testutil.create_datetime_from_weekday_and_hour(0, 9)
        booking_request = Booking(requestCategory=util.CAT_PHYSIO, requestLocation='mtl-downtown', requestDateTime=next_monday_at_9)
        
        providers = db_book.find_providers_for_booking_request(booking_request)
        
        start_years = map(lambda x: x.start_year, providers)
        logging.info('start years %s' % start_years)