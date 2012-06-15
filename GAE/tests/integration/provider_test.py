# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db
from data.model import User

class ProviderTest(BaseTest):
    def test_provider_schedule_set_one_timeslot_action_as_provider(self):
        self.login_as_admin()
        self.init_new_provider()
        # fill all sections
        self.fill_new_provider_address_correctly_action()
        self.fill_new_provider_profile_correctly_action()
        self.solicit_provider()
        self.logout_admin()
        # terms agreement
        self.activate_provider_from_email()
        self.logout_provider()
        
        self.login_as_provider()
        self.provider_schedule_set_one_timeslot_action()


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
        response = self.testapp.get('/provider/bookings', request_variables)
        # patient name in navbar
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain('Rendez-vous')
        response.mustcontain('Horaire')
        assert 'Administration' not in response 
        assert 'Profile' not in response 
        assert 'Addresse' not in response 


        
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
        user = User.query(User.key == provider.user).get()
        activation_url = '/user/activation/%s' % user.signup_token
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
        user = User.query(User.key == provider.user).get()
        activation_url = '/user/activation/%s' % user.signup_token
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


    def test_provider_accept_terms_navigate_away(self):
        self.login_as_admin()
        # init a provider
        self.init_new_provider()
        # fill all sections
        self.fill_new_provider_address_correctly_action()
        self.fill_new_provider_profile_correctly_action()
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
        
        terms_form.submit()
        
        # navigate away and back
        
        # request same page
        user = User.query(User.key == provider.user).get()
        activation_url = '/user/activation/%s' % user.signup_token
        terms_response = self.testapp.get(activation_url)
        
        terms_response.mustcontain("J'accepte les conditions d'utilisation")
        assert "Terms agreed on" not in terms_response
        
        terms_form = terms_response.forms[0]
        terms_form['terms_agreement'] = '1'
        terms_response = terms_form.submit()
        terms_response.mustcontain('Choisissez votre mot de passe')




    def test_upload_image_to_correct_address(self):
        ''' Upload a test image for the new provider '''
        
        self.login_as_admin()
        # init a provider
        self.init_new_provider()
        # fill all sections
        self.fill_new_provider_address_correctly_action()
        self.fill_new_provider_profile_correctly_action()

        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/admin/provider/address', request_variables)
                
        photo_form = response.forms[1] # photo form
        
        photo_form['profilePhoto'] = ('profilePhoto', 'provider-test-image.png')

     #   response = photo_form.submit()
     #   response.showbrowser()
        

    def test_provider_solicit_activation_link_disabled_after_set_password(self):
        self.login_as_admin()
        # init a provider
        self.init_new_provider()
        # fill all sections
        self.fill_new_provider_address_correctly_action()
        self.fill_new_provider_profile_correctly_action()
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
        password_choice_response.mustcontain('Choisissez votre mot de passe')
        password_form = password_choice_response.forms[0]
        password_form['password'] = 'abcdef'
        password_form['password_confirm'] = 'abcdef'
        
        # password has been set
        welcome_response = password_form.submit()
        welcome_response.mustcontain("Rendez-vous")

        self.logout_provider()
        
        response = self.testapp.get(activation_url)
        
        assert "J'accepte les conditions d'utilisation" not in response
        response.mustcontain("Activation link has expired.")
        response.mustcontain("Connexion à veosan")
        response.mustcontain("Couriel")
        response.mustcontain("Mot de passe")

        
                            
    def test_provider_reset_password(self):
        self.create_complete_provider_profile()
        self.logout_admin()
        self.logout_provider()
        
        login_response = self.testapp.get("/login")

        resetpassword_form = login_response.forms[2] # reset passwod is 3rd form on page
        resetpassword_form['email'] = self._TEST_PROVIDER_EMAIL
        response = resetpassword_form.submit()
        
        # terms agreement                       
        response.mustcontain("Password reset instructions sent to %s" % self._TEST_PROVIDER_EMAIL)
        
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(2, len(messages))
        m = messages[1]    

        user = db.get_user_from_email(self._TEST_PROVIDER_EMAIL)

        self.assertEqual(m.subject, 'veosan - password reset instructions' )
        self.assertEqual(m.sender, 'cliktester@gmail.com')
        self.assertIn('Please click the link below to choose a new password', m.body.payload)

        self.assertTrue('/user/resetpassword/%s' % user.resetpassword_token in m.body.payload)

        # terms page
        reset_url = '/user/resetpassword/%s' % user.resetpassword_token
        reset_response = self.testapp.get(reset_url)
        
        reset_response.mustcontain("Choisissez votre mot de passe")
        reset_response.mustcontain(self._TEST_PROVIDER_EMAIL)

        # set password and all that
        password_form = reset_response.forms[0]
        password_form['password'] = '654321'
        password_form['password_confirm'] = '654321'

        reset_post_response = password_form.submit()
        self.assertEqual(reset_post_response.status_int, 200)
        
        reset_post_response.mustcontain('Welcome back! Password has been reset for %s' % user.get_email())
        reset_post_response.mustcontain('Rendez-vous')

        # try to login with old credentials
        logout_response = self.testapp.get("/logout")
        logout_response = logout_response.follow()
        logout_response.mustcontain('Trouvez des soins')
        
        login_response = self.testapp.get("/login")

        login_form = login_response.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD        
        response = login_form.submit()


        # login should fail
        response.mustcontain("rifier votre email et mot de passe.")

        # login again with new credentials
        resetpassword_form = response.forms[0]
        resetpassword_form['email'] = self._TEST_PROVIDER_EMAIL
        resetpassword_form['password'] = '654321'        
        response = resetpassword_form.submit()
        
        # follow response redirect after successful login
        response = response.follow()
        response.mustcontain("Rendez-vous")

    def test_provider_reset_password_twice_with_same_token(self):
        self.create_complete_provider_profile()
        self.logout_admin()
        self.logout_provider()
        
        login_response = self.testapp.get("/login")

        resetpassword_form = login_response.forms[2] # reset passwod is 3rd form on page
        resetpassword_form['email'] = self._TEST_PROVIDER_EMAIL
        response = resetpassword_form.submit()
        
        # terms agreement                       
        response.mustcontain("Password reset instructions sent to %s" % self._TEST_PROVIDER_EMAIL)
        
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(2, len(messages))
        m = messages[1]    

        user = db.get_user_from_email(self._TEST_PROVIDER_EMAIL)

        self.assertEqual(m.subject, 'veosan - password reset instructions')
        self.assertEqual(m.sender, 'cliktester@gmail.com')
        self.assertIn('Please click the link below to choose a new password', m.body.payload)

        self.assertTrue('/user/resetpassword/%s' % user.resetpassword_token in m.body.payload)

        # terms page
        reset_url = '/user/resetpassword/%s' % user.resetpassword_token
        reset_response = self.testapp.get(reset_url)
        
        reset_response.mustcontain("Choisissez votre mot de passe")
        reset_response.mustcontain(self._TEST_PROVIDER_EMAIL)

        # set password and all that
        password_form = reset_response.forms[0]
        password_form['password'] = '654321'
        password_form['password_confirm'] = '654321'

        reset_post_response = password_form.submit()
        self.assertEqual(reset_post_response.status_int, 200)
        
        reset_post_response.mustcontain('Welcome back! Password has been reset for %s' % user.get_email())
        reset_post_response.mustcontain('Rendez-vous')

        # try to re-use the same password reset token
        reset_response = self.testapp.get(reset_url)
        reset_response.mustcontain("Links are expired after 24 hours, please try again")

if __name__ == "__main__":
    unittest.main()
    
    
