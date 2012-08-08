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
        self.login_as_admin()
        self.init_new_provider()
        self.fill_new_provider_address_correctly_action()
        
    def test_fill_new_provider_profile_correctly(self):
        ''' fill out the new provider's profile '''
        
        # init a provider
        self.login_as_admin()
        self.init_new_provider()
        self.fill_new_provider_profile_correctly_action()

    def test_fill_new_provider_address_then_modify(self):
        ''' fill out the new provider's address then modify it '''
        
        # init a provider
        self.login_as_admin()
        self.init_new_provider()
        self.fill_new_provider_address_correctly_action()
        self.modify_provider_address_action()

        
    def test_provider_schedule_set_one_timeslot(self):
        ''' Enable bookings in one timeslot '''
        
        # init a provider
        self.login_as_admin()
        self.init_new_provider()
        self.provider_schedule_set_one_timeslot_action()
        
        
    def test_admin_provider_init_with_duplicate_email(self):
        self.create_complete_provider_profile()

        # log back in as admin        
        self.login_as_admin()
        
        # try to create another profile with the same email address
        request_variables = { 'provider_email' : self._TEST_PROVIDER_EMAIL, 'vanity_url' : 'different_one' }
        response = self.testapp.post('/admin/provider/init', request_variables)
                
        # check for error message
        response.mustcontain("Provider already exists for email address")
        
        
    def test_admin_provider_init_with_empty_email(self):
        ''' initialize a new provider with no email address (should not be possible) '''
        
        self.login_as_admin()
                
        request_variables = { 'provider_email' : '' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        
        # this should fail with an error message
        
        # check for error message
        response.mustcontain("Adresse courriel invalide.")
        
        # if anything below here is in the response, it's not good!
    
        # Check signs of success
        if "Initialized new provider for " in response:
            self.assertTrue(False, "A provider was created without an email address")


    def test_admin_provider_init_with_invalid_email(self):
        ''' initialize a new provider with invalid address (should not be possible) '''
        
        self.login_as_admin()

        request_variables = { 'provider_email' : 'aaabbbccc' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        
        # this should fail with an error message
        
        # check for error message
        response.mustcontain("Adresse courriel invalide.")
        
        # if anything below here is in the response, it's not good!
    
        # Check signs of success
        if "Initialized new provider for " in response:
            self.assertTrue(False, "A provider was created without an email address")
            
            
            
    def test_admin_provider_init_with_duplicate_vanity_url(self):
        self.create_complete_provider_profile()

        # log back in as admin        
        self.login_as_admin()
        
        # try to create another profile with the same vanity url address
        request_variables = { 'provider_email' : 'differe@one.com', 'vanity_url' : self._TEST_PROVIDER_VANITY_URL }
        response = self.testapp.post('/admin/provider/init', request_variables)
                
        # check for error message
        response.mustcontain("That name is already taken, please choose another one.")
        
    def test_admin_provider_init_with_reserved_vanity_url(self):
        # log back in as admin        
        self.login_as_admin()
        
        # try to create another profile with the same vanity url address
        request_variables = { 'provider_email' : self._TEST_PROVIDER_EMAIL, 'vanity_url' : 'admin' }
        response = self.testapp.post('/admin/provider/init', request_variables)
                
        # check for error message
        response.mustcontain("That URL contains a reserved word.")
        
        request_variables = { 'provider_email' : self._TEST_PROVIDER_EMAIL, 'vanity_url' : 'provider' }
        response = self.testapp.post('/admin/provider/init', request_variables)
                
        # check for error message
        response.mustcontain("That URL contains a reserved word.")

        request_variables = { 'provider_email' : self._TEST_PROVIDER_EMAIL, 'vanity_url' : 'login' }
        response = self.testapp.post('/admin/provider/init', request_variables)
                
        # check for error message
        response.mustcontain("That URL contains a reserved word.")

            
    ''' Not relevant anymore - they fill their own profile

    def test_new_provider_solicit_with_empty_profile(self):
        # set things up
        self.login_as_admin()
        self.init_new_provider()

        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        response = self.testapp.get('/admin/provider/admin/%s' % provider.vanity_url)

        response.mustcontain('Provider Administration')
        response.mustcontain(self._TEST_PROVIDER_EMAIL)

        # hit the solicit button
        response = self.testapp.get('/admin/provider/solicit/' + self._TEST_PROVIDER_VANITY_URL)
        
        # check error message is displayed
        response.mustcontain("Incomplete profile")

        # make sure no email is sent
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(0, len(messages)) '''

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
        self.create_complete_provider_profile()
        self.logout_provider()
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
        response.mustcontain("Current status is client_enabled")
        
        status_form = response.forms[0]
        status_form['status'] = 'client_suspended'
        disabled_response = status_form.submit()

        disabled_response.mustcontain("Current status is client_suspended")

        self.logout_admin()
        
        # now try to make a booking with this guy        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        response = self.book_appointment('osteopath', testutil.next_monday_date_string() , 14)
        
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
        response.mustcontain('4:00')
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
        response.mustcontain('4:00')
        # response.mustcontain(...monday...)


    def test_admin_booking_dashboard_patient_profile_abandon(self):
        ''' Visitor chose a provider, filled their email, didn't fill the profile '''
        
        self.create_complete_provider_profile()
        booking_response = self.book_appointment('osteopath', testutil.next_monday_date_string(), 8)
        new_patient_response = self.fill_booking_email_form(booking_response, self._TEST_PATIENT_EMAIL)

        self.logout_patient()                
        self.login_as_admin()

        response = self.testapp.get('/admin/bookings')
        response.mustcontain('Unfilled profile')
        response.mustcontain('4:00')
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
        response.mustcontain('4:00')
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
    
    
