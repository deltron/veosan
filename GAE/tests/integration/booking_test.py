# -*- coding: utf-8 -*-

from admin_test import AdminTest
from datetime import datetime, date
import unittest

class BookingTest(AdminTest):
    ''' TODO: bug because this extends the admin_test it runs everything twice... '''
    
    def test_booking_single_timeslot_available(self):
        AdminTest.test_complete_profile_creation(self)
        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        
        # go back to the main page and try to book tuesday 10am
        response = self.testapp.post('/')
                
        # fill out the form
        booking_form = response.forms[0] # booking form
        booking_form['category'] = 'osteopath' # admin test created an osteopath
        
        booking_date_select = booking_form.fields['booking_date'][0]
        
        # find the option value with a monday

        for (date_string, selected) in booking_date_select.options:
            d = datetime.strptime(date_string, "%Y-%m-%d")
            if d.weekday() == 0: # choose the first monday on the form
                booking_form['booking_date'] = date_string
                break
        
        # leave time to default (should be 8-9h)

        # leave region to default (should be downtown)
        
        response = booking_form.submit()
        
        
        
        self.assertTrue(False, "TODO: why are there no availabilities?")



if __name__ == "__main__":
    unittest.main()
    
    
