# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderSocialTest(BaseTest):
    def test_invite_provider(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        
        response = self.testapp.get('/provider/social/' + self._TEST_PROVIDER_VANITY_URL)

        invite_provider_form = response.forms['invite_provider_form']
        invite_provider_form['first_name'] = 'david'
        invite_provider_form['last_name'] = 'mctest'
        invite_provider_form['email'] = 'mctest@veosan.com'
        
        # default no note
        
        response = invite_provider_form.submit()
        response.mustcontain("Invitation sent to %s %s (%s)" % ('david', 'mctest', 'mctest@veosan.com'))



        messages = self.mail_stub.get_sent_messages(to='mctest@veosan.com')
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Invitation to join Veosan from %s %s' % ('first', 'last'))
        self.assertEqual(m.sender, 'first last <support@veosan.com>')
        self.assertEqual(m.reply_to, self._TEST_PROVIDER_EMAIL)
        self.assertIn('Please click on the link below to create your profile', m.body.payload)
        self.assertIn("I've been using Veosan and thought you might like to try it out. Here's an invitation to create an account.", m.body.payload)

        invite = db.get_invite_from_email('mctest@veosan.com')

        self.assertTrue('/invite/%s' % invite.token in m.body.payload)

        # click the link
        response = self.testapp.get('/invite/' + invite.token)

        # make sure form is pre-populated from email
        signup_form = response.forms['provider_signup_form']
        self.assertEquals(signup_form['first_name'].value, 'david')
        self.assertEquals(signup_form['last_name'].value, 'mctest')
        self.assertEquals(signup_form['email'].value, 'mctest@veosan.com')
        
        # check invite status update
        invite = db.get_invite_from_email('mctest@veosan.com')
        self.assertTrue(invite.link_clicked)

        # add postal code
        signup_form['postal_code'] = 'H1H2C2'
        response2 = signup_form.submit()
        
        signup_form2 = response2.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        welcome_response = signup_form2.submit().follow()

        # should be on the welcome page
        welcome_response.mustcontain("Bienvenue!")
        welcome_response.mustcontain("Comment naviguer sur le site")

        # check invite status update
        invite = db.get_invite_from_email('mctest@veosan.com')
        self.assertTrue(invite.profile_created)


    def test_invite_token_already_used(self):
        pass
    
if __name__ == "__main__":
    unittest.main()
    
    
