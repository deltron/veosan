# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderTest(BaseTest):
    
    def test_add_time_to_schedule(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)

        schedule_form = response.forms['schedule_form']
        
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 9
        schedule_form['end_time'] = 17

        response = schedule_form.submit()
        
        # check on the schedule admin page
        response.mustcontain('9 AM-5 PM')

    def test_delete_time_from_schedule(self):
        pass
    
    def test_change_time_in_schedule(self):
        pass
    
    def test_end_time_before_start_time(self):
        pass

    def test_display_hour_range_int_table(self):
        pass

    def test_click_plus_on_tuesday_10am(self):
        # verify modal is populated with correct info
        pass

    def test_merge_overlapping_times(self):
        # verify modal is populated with correct info
        pass

    def test_merge_overlapping_times(self):
        pass

if __name__ == "__main__":
    unittest.main()
    
    
