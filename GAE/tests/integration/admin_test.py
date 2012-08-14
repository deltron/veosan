# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from base import BaseTest
from data import db
import testutil, util

class AdminTest(BaseTest):
    
    def test_complete_profile_creation(self):
        ''' basic test to complete entire provider profile, the base case '''
        self.create_complete_provider_profile()

   
    def test_fill_new_provider_address_correctly(self):
        ''' fill out the new provider's address '''
        
        # init a provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.fill_new_provider_address_correctly_action()
        
    def test_fill_new_provider_profile_correctly(self):
        ''' fill out the new provider's profile '''
        
        # init a provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.fill_new_provider_profile_correctly_action()

    def test_fill_new_provider_address_then_modify(self):
        ''' fill out the new provider's address then modify it '''
        
        # init a provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.fill_new_provider_address_correctly_action()
        self.modify_provider_address_action()

        
    def test_provider_schedule_set_one_timeslot(self):
        ''' Enable bookings in one timeslot '''
        
        # init a provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.provider_schedule_set_one_timeslot_action()
        
        

    def test_bookings_page_as_admin(self):
        # TODO create a booking
        #import booking_test
        #bt = booking_test.BookingTest()
        #bt.test_booking_new_patient()
        #bt.logout_patient()
        # login as admin and test
        self.login_as_admin()
        response = self.testapp.get('/admin')
        bookings_page = response.follow()
        bookings_page.mustcontain('Rendez-vous')
        
        
    def test_no_bookings_page_as_anonymnous(self):
        self.logout_admin()
        response = self.testapp.get('/admin')
        # check if redirect to admin login page
        self.assertEqual(response.status_int, 302)  
    

    def test_admin_sees_all_tabs_for_provider(self):
        # setup a provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        # login as admin
        self.login_as_admin()
        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        # request the address page
        response = self.testapp.get('/provider/bookings/%s' % provider.vanity_url)
        # patient name in navbar
        response.mustcontain('Administration')
        response.mustcontain('Rendez-vous')
        response.mustcontain('Horaire')
        response.mustcontain('Profil')
        response.mustcontain('Adresse')


    def test_provider_disable(self):       
        self.create_complete_provider_profile()
        self.login_as_admin()
        
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        response = self.testapp.get('/admin/provider/admin/%s' % provider.vanity_url)

        # make sure provider starts as prospect
        response.mustcontain("Current status is prospect")
        
        status_form = response.forms[0]
        status_form['status'] = 'client_suspended'
        disabled_response = status_form.submit()

        disabled_response.mustcontain("Current status is client_suspended")

        self.logout_admin()
        
        # now try to make a booking with this guy        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        response = self.book_appointment('osteopath', testutil.next_monday_date_string() , 18)
        
        # verify error messages
        response.mustcontain("Malheureusement, il n'y a pas de professionnels disponibles qui répondent à vos besoins")
        
        # now enable him again and try to make a booking
        self.login_as_admin()
        
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        response = self.testapp.get('/admin/provider/admin/%s' % provider.vanity_url)
        
        status_form = response.forms[0]
        status_form['status'] = 'client_enabled'
        enabled_response = status_form.submit()
        
        enabled_response.mustcontain("Current status is client_enabled")
        
        # Booking should work
        response = self.book_appointment('osteopath', testutil.next_monday_date_string() , 14)
        response.mustcontain("M. Fantastic F.")

    def test_admin_booking_dashboard_provider_and_patient_confirmed(self):
        ''' The base case, a patient made an appointment and confirmed it '''
        
        self.create_complete_provider_profile()
        booking_response = self.book_appointment('osteopath', testutil.next_monday_date_string(), 8)
        
        # fill out patient profile, receive email and set password
        new_patient_response = self.fill_booking_email_form(booking_response, self._TEST_PATIENT_EMAIL)
        booking_confirm_response = self.fill_new_patient_profile(new_patient_response)
        self.check_activation_email_patient()

        self.logout_patient()                
        self.login_as_admin()
        
        response = self.testapp.get('/admin/bookings')
        response.mustcontain(self._TEST_PATIENT_EMAIL)
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain('Ostéopathe')
        response.mustcontain('8:00')
        # response.mustcontain(...monday...)
        
        

    def test_admin_booking_dashboard_patient_dropped_out(self):
        ''' Visitor chose a provider, then never filled their email '''
        
        self.create_complete_provider_profile()
        booking_response = self.book_appointment('osteopath', testutil.next_monday_date_string(), 8)

        self.logout_patient()                
        self.login_as_admin()

        response = self.testapp.get('/admin/bookings')
        response.mustcontain('User dropped out')
        response.mustcontain('No provider')
        response.mustcontain('No provider booked')
        response.mustcontain('8:00')
        # response.mustcontain(...monday...)


    def test_admin_booking_dashboard_patient_profile_abandon(self):
        ''' Visitor chose a provider, filled their email, didn't fill the profile '''
        
        self.create_complete_provider_profile()
        booking_response = self.book_appointment('osteopath', testutil.next_monday_date_string(), 10)
        new_patient_response = self.fill_booking_email_form(booking_response, self._TEST_PATIENT_EMAIL)

        self.logout_patient()                
        self.login_as_admin()

        response = self.testapp.get('/admin/bookings')
        response.mustcontain('Unfilled profile')
        response.mustcontain('10:00') # this is the wrong time - need to fix time zone stuff
        response.mustcontain(self._TEST_PATIENT_EMAIL)
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain('Ostéopathe')


    def test_admin_booking_dashboard_patient_unconfirmed(self):
        ''' Visitor chose a provider, filled their email, filled the profile but didn't click the email link '''
        
        self.create_complete_provider_profile()
        booking_response = self.book_appointment('osteopath', testutil.next_monday_date_string(), 8)
        new_patient_response = self.fill_booking_email_form(booking_response, self._TEST_PATIENT_EMAIL)
        booking_confirm_response = self.fill_new_patient_profile(new_patient_response)

        self.logout_patient()                
        self.login_as_admin()

        response = self.testapp.get('/admin/bookings')
        response.mustcontain('Patient not confirmed')
        response.mustcontain('8:00')
        response.mustcontain(self._TEST_PATIENT_EMAIL)
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain('Ostéopathe')

    def test_admin_booking_dashboard_no_provider_booked(self):
        ''' No provider was available for the requested date/time '''

        self.create_complete_provider_profile()
        booking_response = self.book_appointment('physiotherapy', testutil.next_monday_date_string(), 17)
        
        self.logout_patient()                
        self.login_as_admin()
        response = self.testapp.get('/admin/bookings')
        # admin booking shows no results
        #response.showbrowser()
        response.mustcontain('No search results')


if __name__ == "__main__":
    unittest.main()
    
    
