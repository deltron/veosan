# -*- coding: utf-8 -*-

from admin_test import AdminTest
from datetime import datetime, date
import unittest

class BookingTest(AdminTest):
    ''' TODO: bug because this extends the admin_test it runs everything twice... '''
    
    def test_booking_single_timeslot_not_available(self):
        AdminTest.test_complete_profile_creation(self)
        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        
        # go back to the main page and try to book tuesday 10am
        response = self.testapp.post('/')
        
        # fill out the form
        booking_form = response.forms[0] # booking form
        booking_form['category'] = 'osteopath' # admin test created an osteopath
        
        booking_date_select = booking_form.fields['booking_date'][0]
        
        # find the option value with a tuesday
        for (date_string, selected) in booking_date_select.options:
            d = datetime.strptime(date_string, "%Y-%m-%d")
            if d.weekday() == 1: #tuesday
                print date_string + " is a tuesday"

        
        



if __name__ == "__main__":
    unittest.main()
    
    
