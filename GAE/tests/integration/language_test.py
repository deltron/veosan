# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db
from data.model import User

class LanguageTest(BaseTest):

    def test_provider_switch_languages_before_setting_password(self):
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
        user = User.query(User.key == provider.user).get()
        activation_url = '/user/activation/%s' % user.signup_token
        terms_response = self.testapp.get(activation_url)
        terms_response.mustcontain("J'accepte les conditions d'utilisation")
        terms_form = terms_response.forms[0]
        terms_form['terms_agreement'] = '1'
        
        # password page
        password_choice_response = terms_form.submit()
        
        # now change language (default is french, so this should switch to english)
        # set the referer header manually (language switching depends on referer)
        headers = { 'referer': '/provider/terms' }
        english_password_response = self.testapp.get('/lang/en', headers=headers)
        redirect_response = english_password_response.follow()
        redirect_response.mustcontain("Choose your password")

if __name__ == "__main__":
    unittest.main()
    
    
