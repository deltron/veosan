# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db
from data.model import User

class ProviderTest(BaseTest):
    def test_provider_schedule_set_one_timeslot_action_as_provider(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        
        # fill all sections
        self.fill_new_provider_address_correctly_action()
        self.fill_new_provider_profile_correctly_action()

        self.provider_schedule_set_one_timeslot_action()


    def test_administration_tab_not_visible_to_provider(self):
        # setup a provider
        self.create_complete_provider_profile()
        self.login_as_provider()

        # request the profile page
        response = self.testapp.get('/provider/profile/%s' % self._TEST_PROVIDER_VANITY_URL)
                
        # patient name in navbar
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain('CV')
        response.mustcontain('Profil')
        response.mustcontain(no='Admin Logout')
        response.mustcontain(no='/provider/admin/')
        assert 'Admin Logout' not in response 


        

    def test_upload_image_to_correct_address(self):
        ''' Upload a test image for the new provider '''
        
        # image upload stub not in WebTest framework yet...
        pass         
        
                            
    def test_provider_reset_password(self):
        self.create_complete_provider_profile()
        self.logout_admin()
        self.logout_provider()
        
        login_response = self.testapp.get("/login")

        resetpassword_form = login_response.forms['resetpassword_form'] # reset passwod is 3rd form on page
        resetpassword_form['email'] = self._TEST_PROVIDER_EMAIL
        response = resetpassword_form.submit()
        
        # terms agreement                       
        response.mustcontain("Un courriel a été envoyé à votre adresse courriel afin de réinitialiser votre mot de passe.")
        
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]    

        user = db.get_user_from_email(self._TEST_PROVIDER_EMAIL)

        self.assertEqual(m.subject, 'Veosan - password reset instructions' )
        self.assertEqual(m.sender, 'support@veosan.com')
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
        reset_post_response = reset_post_response.follow()
        self.assertEqual(reset_post_response.status_int, 200)
        
        reset_post_response.mustcontain('Welcome back! Password has been reset.')
        reset_post_response.mustcontain('Profil')

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
        response.mustcontain("Profil")

    def test_provider_reset_password_twice_with_same_token(self):
        self.create_complete_provider_profile()
        self.logout_admin()
        self.logout_provider()
        
        login_response = self.testapp.get("/login")

        resetpassword_form = login_response.forms['resetpassword_form'] # reset passwod is 3rd form on page
        resetpassword_form['email'] = self._TEST_PROVIDER_EMAIL
        response = resetpassword_form.submit()
        
        # terms agreement                       
        response.mustcontain("Un courriel a été envoyé à votre adresse courriel afin de réinitialiser votre mot de passe.")
        
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]    

        user = db.get_user_from_email(self._TEST_PROVIDER_EMAIL)

        self.assertEqual(m.subject, 'Veosan - password reset instructions')
        self.assertEqual(m.sender, 'support@veosan.com')
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
        reset_post_response = reset_post_response.follow()

        self.assertEqual(reset_post_response.status_int, 200)
        
        reset_post_response.mustcontain('Welcome back! Password has been reset.')
        reset_post_response.mustcontain('Profil')

        # try to re-use the same password reset token
        reset_response = self.testapp.get(reset_url)
        reset_response.mustcontain("Links are expired after 24 hours, please try again")

    def test_disabled_welcome_page(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        
        self.login_as_provider()
        
        # disable the welcome page
        response = self.testapp.get("/provider/welcome/%s/disable" % self._TEST_PROVIDER_VANITY_URL)
        response = response.follow()
        response.mustcontain(no="Bienvenue!")        
        response.mustcontain(no="Comment naviguer sur le site")
        response.mustcontain("Les prochaines étapes")        
        
        self.logout_provider()
        
        response = self.testapp.get('/login')
        
        login_form = response.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect = login_form.submit()
        response = login_redirect.follow()
        
        # make sure we don't land on the welcome page but the profile page instead
        response.mustcontain(no="Comment naviguer sur le site")
        response.mustcontain("Les prochaines étapes")        
        

if __name__ == "__main__":
    unittest.main()
    
    
