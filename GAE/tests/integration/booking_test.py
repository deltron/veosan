# -*- coding: utf-8 -*-

from base import BaseTest
from datetime import datetime, timedelta
import unittest
import util, testutil
from data import db
from webapp2_extras.i18n import format_date, format_datetime
from webapp2_extras import i18n


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
        response.mustcontain("at their clinic at 123 Main St. in Westmount")
        
        # verify date and time
        response.mustcontain("8:00")
    
        d = datetime.strptime(date_string + " 8:00", "%Y-%m-%d %H:%M")

        # how to test this?
        # should be "Mercredi, 12 Fevrier 2012 a 8:00" but days are variable

        #formatted_date = "%s %s %s" % format_datetime(datetime, "EEEE d MMMM yyyy"),  _(u"at"), format_datetime(datetime, "H:mm")
        #response.mustcontain(formatted_date)
    
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
        response.mustcontain("Malheureusement, il n'y a pas de professionnels disponibles qui répondent à vos besoins")


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
        response.mustcontain("at their clinic at 123 Main St. in Westmount")
        # verify date and time
        response.mustcontain("8:00")
    
        d = datetime.strptime(date_string + " 8:00", "%Y-%m-%d %H:%M")

        # ################
        # ################
        # TODO HOW TO TEST??
        
        #formatted_date = "%s %s %s" % format_datetime(datetime, "EEEE d MMMM yyyy"),  "at", format_datetime(datetime, "H:mm")
        #response.mustcontain(formatted_date)
    

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
        response.mustcontain("Malheureusement, il n'y a pas de professionnels disponibles")
        # verify error messages
        self.fail("How should we handle double bookings?")
        #response.showbrowser()
        
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
        
        new_patient_response.mustcontain('Nouveau Patient')
        patient_form = new_patient_response.forms[0]
        patient_form['first_name'] = first_name = 'Pat!'
        patient_form['last_name'] = 'Patient'
 #      patient_form['password'] = self._TEST_PATIENT_PASSWORD
        patient_form['telephone'] = '514-123-1234'
        patient_form['terms_agreement'] = '1'
        booking_confirm_page = patient_form.submit()
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you %s!' % first_name)
         
    def test_booking_existing_patient(self):
        self.test_booking_new_patient()
        self.logout_patient()
        # Try making another booking as Pat the patient
        today = datetime.today()
        next_monday = today + timedelta(days=-today.weekday(), weeks=1)
        next_monday_string = datetime.strftime(next_monday, "%Y-%m-%d")
        # We already have an appointment at 8AM, let's now book 10AM
        result_response = self.book_appointment('osteopath', next_monday_string, '10')
        # email form
        email_form = result_response.forms[0]
        email_form['email'] = self._TEST_PATIENT_EMAIL
        # We are an existing patient, but not logged in, this should take us to the login page
        login_page = email_form.submit()
        login_page.mustcontain('Connexion à Cliksanté')
        login_page.mustcontain('booking_key')
        # email should be set in form
        login_page.mustcontain(self._TEST_PATIENT_EMAIL)
        login_form = login_page.forms[0]
        login_form['password'] = self._TEST_PATIENT_PASSWORD
        login_redirect = login_form.submit()
        booking_confirm_page = login_redirect.follow()
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you Pat!')
        
    def test_booking_with_loggedin_patient(self):
        self.test_booking_new_patient()
        self.logout_patient()
        # Try to login and book another appintment as Pat the patient
        self.login_as_patient()
        # book appointment
        today = datetime.today()
        next_monday = today + timedelta(days=-today.weekday(), weeks=1)
        next_monday_string = datetime.strftime(next_monday, "%Y-%m-%d")
        # We already have an appointment at 8AM, let's now book 10AM
        result_response = self.book_appointment('osteopath', next_monday_string, '10')
        #result_response.showbrowser()
        # email form
        book_form = result_response.forms[0]
        # no email on form (can we assert this?)
        booking_confirm_page = book_form.submit()
        #booking_confirm_page.showbrowser()
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you Pat!')
     
     
    def test_booking_fail_with_provider_without_terms_agreement(self):
        ''' Create a booking in the timeslot after another booking is made in the same timeslot '''
        
        self.create_complete_provider_profile()
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        provider.terms_agreement = False
        provider.terms_date = None
        provider.put()
        # book appointment
        response = self.book_appointment('osteopath', testutil.next_monday_date_string(), '8')
        response.mustcontain('Malheureusement')
        
        
           
        
if __name__ == "__main__":
    unittest.main()
    
    
