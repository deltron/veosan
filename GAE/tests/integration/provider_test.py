# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db 

class ProviderTest(BaseTest):

    def test_administration_tab_not_visible_to_provider(self):
        # setup a provider
        self.create_complete_provider_profile()
        self.logout_provider()
        # login as provider
        self.login_as_provider()
        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/address', request_variables)
        # patient name in navbar
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain('Adresse')
        response.mustcontain('Fantastic')
        response.mustcontain('Fox')
        assert 'Administration' not in response 
        
    def test_provider_solicit_password_too_short(self):
        self.login_as_admin()
        # init a provider
        self.init_new_provider()
        # fill all sections
        self.fill_new_provider_address_correctly_action()
        self.fill_new_provider_profile_correctly_action()
        self.provider_schedule_set_one_timeslot_action()
        # solicit
        self.solicit_provider()
        self.logout_admin()
        
        # terms agreement                       
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        # terms page
        activation_url = 'http://localhost/provider/activation/%s' % provider.activation_key
        terms_response = self.testapp.get(activation_url)
        terms_response.mustcontain("J'accepte les conditions d'utilisation")
        terms_form = terms_response.forms[0]
        terms_form['terms_agreement'] = '1'
        
        # password page
        password_choice_response = terms_form.submit()
        password_choice_response.mustcontain('Choisissez votre mot de passe')
        password_form = password_choice_response.forms[0]
        password_form['password'] = 'abc'
        password_form['password_confirm'] = 'abc'

        welcome_response = password_form.submit()
        self.assertEqual(welcome_response.status_int, 200)
        welcome_response.mustcontain('Password needs at least 6 characters')
                                     
                                     
    def test_provider_solicit_password_not_matched(self):
        self.login_as_admin()
        # init a provider
        self.init_new_provider()
        # fill all sections
        self.fill_new_provider_address_correctly_action()
        self.fill_new_provider_profile_correctly_action()
        self.provider_schedule_set_one_timeslot_action()
        # solicit
        self.solicit_provider()
        self.logout_admin()
        
        # terms agreement                       
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        # terms page
        activation_url = 'http://localhost/provider/activation/%s' % provider.activation_key
        terms_response = self.testapp.get(activation_url)
        terms_response.mustcontain("J'accepte les conditions d'utilisation")
        terms_form = terms_response.forms[0]
        terms_form['terms_agreement'] = '1'
        
        # password page
        password_choice_response = terms_form.submit()
        password_choice_response.mustcontain('Choisissez votre mot de passe')
        password_form = password_choice_response.forms[0]
        password_form['password'] = self._TEST_PROVIDER_PASSWORD
        password_form['password_confirm'] = 'not_matching'

        welcome_response = password_form.submit()
        self.assertEqual(welcome_response.status_int, 200)
        welcome_response.mustcontain('Passwords do not match')



    def test_upload_image_to_correct_address(self):
        ''' Upload a test image for the new provider '''
        
        self.test_fill_new_provider_address_correctly()
        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/address', request_variables)
        
        photo_form = response.forms[1] # photo form
        
        photo_form['profilePhoto'] = ('profilePhoto', 'provider-test-image.png')
        
        self.fail()
        # photo_form.submit()
        
        # hmm can't upload
        # not possible to test blobstore yet...
        

if __name__ == "__main__":
    unittest.main()
    
    
