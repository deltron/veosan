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
        self.self_signup_provider()
        self.fill_new_provider_address_correctly_action()
        
    def test_fill_new_provider_profile_correctly(self):
        ''' fill out the new provider's profile '''
        
        # init a provider
        self.self_signup_provider()
        self.fill_new_provider_profile_correctly_action()

    def test_fill_new_provider_address_then_modify(self):
        ''' fill out the new provider's address then modify it '''
        
        # init a provider
        self.self_signup_provider()
        self.fill_new_provider_address_correctly_action()
        self.modify_provider_address_action()

        
    def test_provider_schedule_set_one_timeslot(self):
        ''' Enable bookings in one timeslot '''
        
        # init a provider
        self.self_signup_provider()
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
        bookings_page.mustcontain('Bookings')
        
        
    def test_no_bookings_page_as_anonymnous(self):
        self.logout_admin()
        response = self.testapp.get('/admin')
        # check if redirect to admin login page
        self.assertEqual(response.status_int, 302)  
    

    def test_admin_sees_all_tabs_for_provider(self):
        # setup a provider
        self.self_signup_provider()
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

    def test_admin_change_password_for_provider(self):
        # setup a provider
        self.self_signup_provider()
        # login as admin
        self.login_as_admin()
        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        # request the admin page
        response = self.testapp.get('/admin/provider/admin/%s' % provider.vanity_url)
        
        password_form = response.forms['change_password']
        password_form['password'] = 'brocolli'
        password_form.submit()
        
        self.logout_admin()
        self.logout_provider()
        
        # login with old password
        login_page = self.testapp.get('/login')
        
        is_french = 'Connexion' in login_page
        is_english = 'Login' in login_page
        
        if is_english:
            login_page.mustcontain(u"Login")
        elif is_french:
            login_page.mustcontain(u"Connexion")
            
        login_form = login_page.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_error = login_form.submit()
        
        login_error.mustcontain("Login failed. Try again.")
        
        login_form = login_error.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = 'brocolli'
        login_success = login_form.submit().follow()

        # default page for provider after login is welcome
        # (in french because profile is set to french)
        login_success.mustcontain("Profil")
        login_success.mustcontain(self._TEST_PROVIDER_EMAIL)
        login_success.mustcontain("Bienvenue!")
        login_success.mustcontain("Comment naviguer sur le site")        

        # check the event log
        #self.assert_msg_in_log("Provider Logged In")

        return response


if __name__ == "__main__":
    unittest.main()
    
    
