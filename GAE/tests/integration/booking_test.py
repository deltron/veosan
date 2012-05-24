# -*- coding: utf-8 -*-

from admin_test import AdminTest
from datetime import datetime, date
import unittest
import util

class BookingTest(AdminTest):
    ''' TODO: bug because this extends the admin_test it runs everything twice... '''
    
    def test_booking_single_timeslot_available(self):
        ''' Create a booking in the available timeslot '''
        
        AdminTest.test_complete_profile_creation(self)
        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        
        # go back to the main page and try to book monday 8am
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
        
        # verify provider name
        response.mustcontain("Mr. Fantastic F.", "is available")
        
        # verify location
        response.mustcontain("at his clinic on 123 Main St. in Westmount")
        
        # verify date and time
        response.mustcontain("8:00")
    
        d = datetime.strptime(date_string + " 8:00", "%Y-%m-%d %H:%M")
        formatted_date = util.format_datetime_full(d)
        response.mustcontain(formatted_date)
    
        # verify bio and quote
        response.mustcontain("The quick brown fox jumped over the lazy dog")
        response.mustcontain("Areas of interest include treatment and management of spinal conditions with an emphasis on manual therapy and rehabilitative exercise.")
        


if __name__ == "__main__":
    unittest.main()
    
    
