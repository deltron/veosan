# -*- coding: utf-8 -*-
import unittest
from base import BaseTest
from data import db


class AuthenticationTest(BaseTest):
     
    def test_provider_login_success(self):
        ''' login with provider credentials '''
        # Create provider and logout
        self.create_complete_provider_profile()
        self.logout_provider()
        # Now login again
        response = self.testapp.get('/login')
        # verify we get the login page
        response.mustcontain(u"Login")
        # fill out details
        login_form = response.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain(self._TEST_PROVIDER_EMAIL)
        # login lands on booking page
        login_welcome_page.mustcontain('Profil')
        
        #check if user last login has been updated
        self.login_as_admin()
        response = self.testapp.get('/admin/providers')
        
        # err, how to check?
        

    def test_provider_login_fail(self):
        # Create provider and logout
        self.create_complete_provider_profile()
        self.logout_provider()
        # Now login again
        response = self.testapp.get('/login')
        # verify we get the login page
        response.mustcontain("Login")
        # fill out details
        login_form = response.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = 'This is the wrong password'
        login_failed_response = login_form.submit()
        # return to login page
        login_failed_response.mustcontain("Login")
        # message about failed login
        login_failed_response.mustcontain("Login failed. Try again.")
        

    def test_patient_login_success(self):
        '''
            Test that patients can login
        '''
        # Create patient in datastore
        self.create_test_patient()
        # login as patient
        response = self.testapp.get('/login')
        response.mustcontain("Login")
        login_form = response.forms[0]
        login_form['email'] = self._TEST_PATIENT_EMAIL
        login_form['password'] = self._TEST_PATIENT_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # login lands on index page
        login_welcome_page.mustcontain('Rendez-vous à venir')

    def test_patient_login_fail(self):
        # Create patient in datastore
        self.create_test_patient()
        # Try to login and book another appintment as Pat the patient
        self.login_as_patient()
        # login as patient
        
        response = self.testapp.get('/login')
        response.mustcontain("Connexion")
        login_form = response.forms[0]
        login_form['email'] = self._TEST_PATIENT_EMAIL
        login_form['password'] = 'This is the wrong password for the patient'
        login_failed_response = login_form.submit()
        # response after login is a redirect, so follow
        # return to login page
        login_failed_response.mustcontain("Connexion")
        # message about failed login
        login_failed_response.mustcontain("rifier votre email et mot de passe.")
        
    def test_provider_login_after_admin(self):
        ''' login with provider credentials '''
        # Create provider and logout
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        # Now login again
        response = self.testapp.get('/login')
        # verify we get the login page
        response.mustcontain(u"Logged in as admin already.")
        response.mustcontain(no="password")
        response.mustcontain(no="submit")

    def test_admin_login_after_provider(self):
        ''' login with provider credentials '''
        # Create provider and logout
        self.create_complete_provider_profile()
        
        self.login_as_admin()
        response = self.testapp.get('/admin').follow()

        response.mustcontain('Dashboard')
        
        # check for evidence provider is logged out
        response.mustcontain('My Account')
        
        response = self.testapp.get('/admin/providers')

        # try to navigate a provider
        response.mustcontain('firstlast')
        
        # check menu headers
        response = self.testapp.get('/provider/profile/firstlast')
        response.mustcontain('/provider/address/firstlast')
        response.mustcontain('/provider/cv/firstlast')
        response.mustcontain('/provider/schedule/firstlast')


if __name__ == "__main__":
    unittest.main()
            