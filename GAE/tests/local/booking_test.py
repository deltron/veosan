
import logging
from test_data import create_test_providers
from base_test import BaseTestCase
from data.db import Provider

class BookingTestCase(BaseTestCase):
    
    def test_find_best_provider_without_perfect_match(self):
        providers = create_test_providers()
        logging.info("providers: %s" % providers)
        print len(providers)
        print Provider.query().count()
        self.assertEqual(len(providers), Provider.query().count())