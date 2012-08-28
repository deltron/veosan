# -*- coding: utf-8 -*-

from base import BaseTest
from datetime import datetime, timedelta
import unittest
import testutil, util
from data import db
from data.model import Patient, Booking, User
import logging


class BookingTest(BaseTest):
    
    def test_booking_single_timeslot_available(self):
        ''' Create a booking in the available timeslot '''
        self.create_complete_provider_profile()
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # try to book monday 8am
        response = self.book_appointment('osteopath', testutil.next_monday_date_string(), 10)
        # verify provider name
        response.mustcontain("M. Fantastic F.")
        # verify location
        response.mustcontain("123 Main St.")
        response.mustcontain("Westmount")
        # verify date and time
        response.mustcontain("6:00") # this is wrong time - not time zone aware
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
        booking_response = self.book_appointment('osteopath', testutil.next_weekday_date_string(testutil.MONDAY), 10)

        # verify provider name
        booking_response.mustcontain("M. Fantastic F.")
        # verify location
        booking_response.mustcontain("123 Main St.")
        booking_response.mustcontain("Westmount")
        # verify date and time
        booking_response.mustcontain("6:00") # this is the wrong time - not time zone aware

        # fill out patient profile, receive email and set password
        new_patient_response = self.fill_booking_email_form(booking_response, self._TEST_PATIENT_EMAIL)
        booking_confirm_response = self.fill_new_patient_profile(new_patient_response)
        self.check_activation_email_patient()

        
        # now try to book again
        # go back to the main page and try to book monday 8am again
        response = self.book_appointment('osteopath', testutil.next_weekday_date_string(testutil.MONDAY), 8)

        # get the next slot
        response.mustcontain("9:00")
        response.mustcontain("M. Fantastic F.")
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

    def test_booking_new_patient_reload_sent_page(self):
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

        booking_confirm_response = self.fill_new_patient_profile(new_patient_response)

         
    def test_booking_existing_patient(self):
        self.test_booking_new_patient()
        self.logout_patient()
        # Try making another booking as Pat the patient
        today = datetime.today()
        next_monday = today + timedelta(days= -today.weekday(), weeks=1)
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
        next_monday = today + timedelta(days= -today.weekday(), weeks=1)
        next_monday_string = datetime.strftime(next_monday, "%Y-%m-%d")
        # We already have an appointment at 8AM, let's now book 10AM
        result_response = self.book_appointment('osteopath', next_monday_string, '10')
        # no email on form (can we assert this?)
        booking_confirm_page = self.fill_booking_email_form(result_response, self._TEST_PATIENT_EMAIL)
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you Pat')
     
             
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
        patient_form['terms_agreement'] = False
        booking_confirm_page = patient_form.submit()
        
        booking_confirm_page.mustcontain(u"Le prénom est un champs obligatoire")
        booking_confirm_page.mustcontain(u"Le nom de famille est un champs obligatoire")
        booking_confirm_page.mustcontain(u"You must accept the terms to book an appointment")



    def test_book_from_public_profile_new_patient(self):
        self.create_provider_and_enable_booking()
        # Book from public profile
        date_string = testutil.next_monday_date_string()
        time_string = '10'
        self.book_from_public_profile(date_string, time_string)
        
        # provider should not see the booking yet, check provider bookings list, should be empty as booking is not confirmed
        self.login_as_provider()
        provider_bookings = self.testapp.get('/provider/bookings/' + self._TEST_PROVIDER_VANITY_URL)
        provider_bookings.mustcontain('Vous n’avez aucun rendez-vous prévu')
        # no email sent to provider (patient is not confirmed)
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(0, len(messages))
        self.logout_provider()
        
        # patient confirms
        self.patient_confirms_latest_booking(date_string, time_string)


    def test_public_profile_book_no_password_returning_patient(self):
        self.create_provider_and_enable_booking()
        # book once from public profile
        date_string = testutil.next_monday_date_string()
        time_string = '10'
        self.book_from_public_profile(date_string, time_string)
        
        # provider should not see the booking yet, check provider bookings list, should be empty as booking is not confirmed
        self.login_as_provider()
        provider_bookings = self.testapp.get('/provider/bookings/' + self._TEST_PROVIDER_VANITY_URL)
        provider_bookings.mustcontain('Vous n’avez aucun rendez-vous prévu')
        # no email sent to provider (patient is not confirmed)
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(0, len(messages))
        self.logout_provider()
        
        self.patient_confirms_latest_booking(date_string, time_string)
        
        # book second time from public profile
        date_string = testutil.next_monday_date_string()
        time_string = '11'
        self.book_from_public_profile(date_string, time_string, returning_patient=True)
        self.patient_confirms_latest_booking(date_string, time_string)
        


    def test_booking_inside_available_schedule(self):
        ''' if someone forces the URL to book something outside available schedule '''
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")

        # Monday 9-12 should be available, let's visit public profile and check
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Lundi")
        response.mustcontain("9:00")
        
        # try to book monday at 10h (which is available)
        next_monday = testutil.next_weekday_date_string(0)
        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book/' + next_monday + '/' + '10')
       
        # should not fail, should be registration page
        response.mustcontain(no="Choisissez la date et l'heure de votre rendez-vous")
        response.mustcontain(no="button"+next_monday)
        response.mustcontain("Nouveau rendez-vous")
        response.mustcontain("Votre rendez-vous")
        response.mustcontain(next_monday)


    def test_booking_outside_available_schedule(self):
        ''' if someone forces the URL to book something outside available schedule '''
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")

        # Monday 9-12 should be available, let's visit public profile and check
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Lundi")
        response.mustcontain("9:00")
        
        # try to book monday at 17h (which is not available)
        next_monday = testutil.next_weekday_date_string(0)
        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book/' + next_monday + '/' + '17')
       
        # should fail and redirect to booking page with list of available times
        response = response.follow()
        response.mustcontain("Choisissez la date et l'heure de votre rendez-vous")
        response.mustcontain("button-"+next_monday+"-9")

    def test_booking_inside_available_schedule_but_booked_by_someone_else(self):
        ''' if someone forces the URL to book something outside available schedule '''
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")

        self.logout_admin()
        
        # book an appointment for next monday at 10am
        next_monday = testutil.next_weekday_date_string(0)
        self.book_from_public_profile(next_monday, 10, False, 
                                      self._TEST_PATIENT_EMAIL, self._TEST_PATIENT_TELEPHONE)
        
        self.patient_confirms_latest_booking(next_monday, 10)
        
        self.logout_patient()
        
        # do it again with another patient (this should fail)
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book/' + next_monday + '/' + '17')
       
        # should fail and redirect to booking page with list of available times
        response = response.follow()
        response.mustcontain("Choisissez la date et l'heure de votre rendez-vous")
        response.mustcontain("button-"+next_monday)        
        

    
    # Test: double booking: one patient with 2 providers at same time

    def test_schedule_display(self):
        ''' Test that schedule is properly displayed '''
        # create provider and add schedules
        self.create_complete_provider_profile()
        self.login_as_provider()
        start_time=9
        self.provider_schedule_set_one_timeslot_action(day='monday', start_time=start_time, end_time=12)
        self.provider_schedule_set_one_timeslot_action(day='wednesday', start_time=start_time, end_time=12)
        self.logout_provider()
        
        # enable booking
        self.login_as_admin()
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")
        self.logout_admin()
        
        # check that all schedule time buttons are there.
        schedule_page = self.testapp.get('/%s/book' % self._TEST_PROVIDER_VANITY_URL)
        monday_date_string = testutil.next_weekday_date_string(0)
        schedule_page.mustcontain('button-%s-%s' % (monday_date_string, start_time))
        wed_date_string = testutil.next_weekday_date_string(2)
        schedule_page.mustcontain('button-%s-%s' % (wed_date_string, start_time))
        
         
if __name__ == "__main__":
    unittest.main()
    
    
