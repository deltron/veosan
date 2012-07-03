# -*- coding: utf-8 -*-
import unittest
from base import BaseTest


class AuthenticationTest(BaseTest):
     
    def test_provider_login_success(self):
        ''' login with provider credentials '''
        # Create provider and logout
        self.create_complete_provider_profile()
        self.logout_provider()
        # Now login again
        response = self.testapp.get('/login')
        # verify we get the login page
        response.mustcontain(u"Connexion")
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
        login_welcome_page.mustcontain('Rendez-vous')
        

    def test_provider_login_fail(self):
        # Create provider and logout
        self.create_complete_provider_profile()
        self.logout_provider()
        # Now login again
        response = self.testapp.get('/login')
        # verify we get the login page
        response.mustcontain("Connexion")
        # fill out details
        login_form = response.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = 'This is the wrong password'
        login_failed_response = login_form.submit()
        # return to login page
        login_failed_response.mustcontain("Connexion")
        # message about failed login
        login_failed_response.mustcontain("rifier votre email et mot de passe.")
        

    def test_patient_login_success(self):
        '''
            Test that patients can login
        '''
        # Create patient in datastore
        self.create_test_patient()
        # login as patient
        response = self.testapp.get('/login')
        response.mustcontain("Connexion")
        login_form = response.forms[0]
        login_form['email'] = self._TEST_PATIENT_EMAIL
        login_form['password'] = self._TEST_PATIENT_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # login lands on index page
        login_welcome_page.mustcontain('Upcoming Appointments')

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
        
           
        
if __name__ == "__main__":
    unittest.main()
            