# -*- coding: utf-8 -*-

from base import BaseTest
from datetime import datetime
import unittest
import util

class BookingTest(BaseTest):
    
    def test_booking_single_timeslot_available(self):
        ''' Create a booking in the available timeslot '''
        
        self.create_complete_provider_profile()
        
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
        
        
    def test_booking_single_timeslot_book_unavailable_time(self):
        ''' Create a booking in a timeslot with no availability '''
        
        self.create_complete_provider_profile()
        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        
        # go back to the main page and try to book monday 8am
        response = self.testapp.post('/')
                
        # fill out the form
        booking_form = response.forms[0] # booking form
        booking_form['category'] = 'osteopath' # admin test created an osteopath
        
        booking_date_select = booking_form.fields['booking_date'][0]
        
        # find the option value with a tuesday (no availability)

        for (date_string, selected) in booking_date_select.options:
            d = datetime.strptime(date_string, "%Y-%m-%d")
            if d.weekday() == 1: # choose the first tuesday on the form
                booking_form['booking_date'] = date_string
                break
        
        # set time to 2pm
        booking_form['booking_time'] = '14'

        # leave region to default (should be downtown)
        
        response = booking_form.submit()
        
        # verify error messages
        response.mustcontain("Fully Booked!")
        response.mustcontain("We currently do not have a health-care professional available that matches your needs and schedule.")
        response.mustcontain("Please fill in your email below and we will contact you as soon as we have availability.")

    def test_booking_twice_in_same_timeslot(self):
        ''' Create a booking in the timeslot after another booking is made in the same timeslot '''
        
        self.create_complete_provider_profile()
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
        
        ## COMPLETE BOOKING
        
        # now try to book again
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
        
        # verify error messages
        self.assertTrue(False, "How should we handle double bookings?")
        
        #response.showbrowser()

        #response.mustcontain("Fully Booked!")
        #response.mustcontain("We currently do not have a health-care professional available that matches your needs and schedule.")
        #response.mustcontain("Please fill in your email below and we will contact you as soon as we have availability.")
       
        
    def test_booking_new_patient(self):
        ''' Create a booking in the available timeslot '''
        
        # setup a provider
        self.create_complete_provider_profile()
        self.logout_provider()
        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # go back to the main page and try to book monday 8am
        result_response = self.testapp.post('/')
        # fill out the form
        booking_form = result_response.forms[0] # booking form
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
        result_response = booking_form.submit()
        # email form
        email_form = result_response.forms[0]
        email_form['email'] = 'pat@patient.com'
        new_patient_response = email_form.submit()
        
        #new_patient_response.showbrowser()
        new_patient_response.mustcontain('Nouveau Patient')
        patient_form = new_patient_response.forms[0]
        patient_form['first_name'] = first_name = 'Pat!'
        patient_form['last_name'] = 'Patient'
        patient_form['password'] = '123456'
        patient_form['telephone'] = '514-123-1234'
        patient_form['terms_agreement'] = '1'
        booking_confirm_page = patient_form.submit()
        
        booking_confirm_page.showbrowser()
        booking_confirm_page.mustcontain('Thank you %s!' % first_name)
        
        
if __name__ == "__main__":
    unittest.main()
    
    
