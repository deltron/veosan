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
        request_variables = { 'provider_email' : self._TEST_PROVIDER_EMAIL }
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
        response.mustcontain("Addresse courriel invalide.")
        
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
        response.mustcontain("Addresse courriel invalide.")
        
        # if anything below here is in the response, it's not good!
    
        # Check signs of success
        if "Initialized new provider for " in response:
            self.assertTrue(False, "A provider was created without an email address")
            

    def test_new_provider_solicit_with_empty_profile(self):
        # set things up
        self.login_as_admin()
        self.init_new_provider()

        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/admin/provider', request_variables)

        response.mustcontain('Provider Administration')
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        solicit_form = response.forms[0]
        # sends an email to the provider
        response = solicit_form.submit()
        
        # check error message is displayed
        response.mustcontain("Incomplete profile")

        # make sure no email is sent
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(0, len(messages))


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
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/bookings', request_variables)
        # patient name in navbar
        response.mustcontain('Administration')
        response.mustcontain('Rendez-vous')
        response.mustcontain('Horaire')
        response.mustcontain('Profile')
        response.mustcontain('Adresse')


    def test_provider_disable(self):
        self.create_complete_provider_profile()
        self.login_as_admin()
        
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/admin/provider', request_variables)
        
        # make sure provider starts as Enabled
        response.mustcontain("Current status is enable=True")
        response.mustcontain("Disable Provider") # button

        disable_form = response.forms[1]
        disable_response = disable_form.submit()
        
        disable_response.mustcontain("Current status is enable=False")
        disable_response.mustcontain("Enable Provider")

        self.logout_admin()
        
        # now try to make a booking with this guy        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        response = self.book_appointment(util.CAT_OSTEO, testutil.next_monday_date_string() , 14)
        
        # verify error messages
        response.mustcontain("Malheureusement, il n'y a pas de professionnels disponibles qui répondent à vos besoins")
        
        # now enable him again and try to make a booking
        self.login_as_admin()
        
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/admin/provider', request_variables)
        
        # make sure provider starts as Enabled
        response.mustcontain("Current status is enable=False")
        response.mustcontain("Enable Provider") # button

        disable_form = response.forms[1]
        disable_response = disable_form.submit()
        
        disable_response.mustcontain("Current status is enable=True")
        disable_response.mustcontain("Disable Provider")        
        
        # Booking should work
        response = self.book_appointment(util.CAT_OSTEO, testutil.next_monday_date_string() , 14)
        response.mustcontain("Mr. Fantastic F.")

    def test_admin_booking_dashboard_provider_and_patient_confirmed(self):
        ''' The base case, a patient made an appointment and confirmed it '''
        self.assertTrue(False, "TODO")

    def test_admin_booking_dashboard_patient_dropped_out(self):
        ''' Patient chose a provider, entered their email in first form, then never filled the profile '''
        self.assertTrue(False, "TODO")

    def test_admin_booking_dashboard_patient_unconfirmed(self):
        ''' Patient chose a provider, filled their profile but didn't click the email link '''
        self.assertTrue(False, "TODO")

    def test_admin_booking_dashboard_no_provider_booked(self):
        ''' No provider was available for the requested date/time '''
        self.assertTrue(False, "TODO")
    
if __name__ == "__main__":
    unittest.main()
    
    
