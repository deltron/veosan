# -*- coding: utf-8 -*-

from base import BaseTest
from datetime import datetime, timedelta
import unittest
import testutil, util
from data import db
from data.model import Patient, Booking, User


class BookingTest(BaseTest):
    
    def test_booking_single_timeslot_available(self):
        ''' Create a booking in the available timeslot '''
        self.create_complete_provider_profile()
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # try to book monday 8am
        response = self.book_appointment('osteopath', testutil.next_monday_date_string(), 8)
        # verify provider name
        response.mustcontain("Mr. Fantastic F.")
        # verify location
        response.mustcontain("123 Main St.")
        response.mustcontain("Westmount")
        # verify date and time
        response.mustcontain("8:00")
        # verify bio and quote
        response.mustcontain("The quick brown fox jumped over the lazy dog")
        response.mustcontain("Areas of interest include treatment and management of spinal conditions with an emphasis on manual therapy and rehabilitative exercise.")
        
        
    def test_booking_single_timeslot_book_unavailable_time(self):
        ''' Create a booking in a timeslot with no availability '''
        self.create_complete_provider_profile()
        # Out Schedule is open only on Monday, try to book Tuesday
        response = self.book_appointment('osteopath', testutil.next_weekday_date_string(testutil.TUESDAY), 14)
        # verify error messages
        response.mustcontain("Malheureusement, il n'y a pas de professionnels disponibles qui répondent à vos besoins")


    def test_booking_twice_in_same_timeslot(self):
        ''' Create a booking in the timeslot after another booking is made in the same timeslot 
            shows next available timeslot?
        '''

        self.create_complete_provider_profile()
        self.logout_provider()
        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # go back to the main page and try to book monday 8am
        booking_response = self.book_appointment('osteopath', testutil.next_weekday_date_string(testutil.MONDAY), 8)

        # verify provider name
        booking_response.mustcontain("Mr. Fantastic F.")
        # verify location
        booking_response.mustcontain("123 Main St.")
        booking_response.mustcontain("Westmount")
        # verify date and time
        booking_response.mustcontain("8:00")

        # fill out patient profile, receive email and set password
        new_patient_response = self.fill_booking_email_form(booking_response, self._TEST_PATIENT_EMAIL)
        booking_confirm_response = self.fill_new_patient_profile(new_patient_response)
        self.check_activation_email_patient()

        
        # now try to book again
        # go back to the main page and try to book monday 8am again
        response = self.book_appointment('osteopath', testutil.next_weekday_date_string(testutil.MONDAY), 8)

        # get the next slot
        response.mustcontain("9:00")
        response.mustcontain("Mr. Fantastic F.")
        response.mustcontain("123 Main St.")
        response.mustcontain("Westmount")

        
    def test_booking_new_patient(self):
        ''' Create a booking in the available timeslot '''
        
        # setup a provider
        self.create_complete_provider_profile()
        self.logout_provider()
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # go back to the main page and try to book monday 8am
        booking_response = self.book_appointment('osteopath', testutil.next_weekday_date_string(testutil.MONDAY), 8)

        # fill out patient profile, receive email and set password
        new_patient_response = self.fill_booking_email_form(booking_response, self._TEST_PATIENT_EMAIL)
        booking_confirm_response = self.fill_new_patient_profile(new_patient_response)
        self.check_activation_email_patient()
        
        # Check that booking is visible on provider's bookings list
        provider_response = self.login_as_provider()
        
        # go to bookings page
        provider_response = self.testapp.get('/provider/bookings/%s' % self._TEST_PROVIDER_VANITY_URL)
                
        # We should already be on the bookings page after the login
        provider_response.mustcontain('Pat Patient')

         
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
        login_page = self.fill_booking_email_form(result_response, self._TEST_PATIENT_EMAIL)
        # We are an existing patient, but not logged in, this should take us to the login page
        login_page.mustcontain('Connexion')
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
        # no email on form (can we assert this?)
        booking_confirm_page = self.fill_booking_email_form(result_response)
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
        
        
    def test_booking_new_patient_terms_not_agreed(self):
        ''' Create a booking in the available timeslot, but don't agree to terms on new patient page '''
        
        # setup a provider
        self.create_complete_provider_profile()
        self.logout_provider()
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # go back to the main page and try to book monday 8am
        response = self.book_appointment('osteopath', testutil.next_weekday_date_string(testutil.MONDAY), 8)
        # email form
        new_patient_response = self.fill_booking_email_form(response, self._TEST_PATIENT_EMAIL)
        
        new_patient_response.mustcontain('Nouveau patient')
        patient_form = new_patient_response.forms[0]
        booking_confirm_page = patient_form.submit()
        
        booking_confirm_page.mustcontain(u"Le prénom est un champs obligatoire")
        booking_confirm_page.mustcontain(u"Le nom de famille est un champs obligatoire")
        booking_confirm_page.mustcontain(u"Le numéro de téléphone doit être dans le format suivant: 514-555-1212")
        booking_confirm_page.mustcontain(u"You must accept the terms to book an appointment")

if __name__ == "__main__":
    unittest.main()
    
    
