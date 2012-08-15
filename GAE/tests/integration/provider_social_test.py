# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderSocialTest(BaseTest):
    def test_invite_provider(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        
        response = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)

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
        self.assertIn("I've been using Veosan and thought you might like to try it out. Here's an invitation to create a profile.", m.body.payload)

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
        signup_form2['category'] = 'dietitian'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        welcome_response = signup_form2.submit().follow()

        # should be on the welcome page
        welcome_response.mustcontain("Bienvenue!")
        welcome_response.mustcontain("Comment naviguer sur le site")

        # check invite status update
        invite = db.get_invite_from_email('mctest@veosan.com')
        self.assertTrue(invite.profile_created)
        
        provider = db.get_provider_from_email('mctest@veosan.com')
        
        # check connection on network page
        response = self.testapp.get('/provider/network/' + provider.vanity_url)
        response.mustcontain('Votre réseau contient 1 professionels de la santé.')
        response.mustcontain('first last')
        response.mustcontain('Ostéopathe')
        self.logout_provider()
        
        # check the originating provider social network
        self.login_as_provider()
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        response = self.testapp.get('/provider/network/' + provider.vanity_url)
        response.mustcontain('Votre réseau contient 1 professionels de la santé.')
        response.mustcontain('david mctest')
        response.mustcontain('Diététicien')



    def test_invite_token_already_used(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        
        response = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)

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
        self.assertIn("I've been using Veosan and thought you might like to try it out. Here's an invitation to create a profile.", m.body.payload)

        invite = db.get_invite_from_email('mctest@veosan.com')
        invite_token = invite.token
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
        
        
        
        
        
        #
                
        invite = db.get_invite_from_email('mctest@veosan.com')
        self.assertTrue(invite.link_clicked)
        self.assertTrue(invite.profile_created)

        # make sure token is burned        
        self.assertIsNone(invite.token)
        
        
        # click the link
        response = self.testapp.get('/invite/' + invite_token)

        # since token was already used (and profile created), go to login page
        login_page = response.follow()
        
        login_page.mustcontain(u"Connexion")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain(self._TEST_PROVIDER_EMAIL)
        login_welcome_page.mustcontain("Bienvenue!")
        login_welcome_page.mustcontain("Comment naviguer sur le site")


    def test_connect_not_logged_in(self):
        # create a provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.logout_provider()
        
        # and another
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'david'
        signup_form['last_name'] = 'mctester'
        signup_form['email'] = 'mctest@veosan.com'
        signup_form['postal_code'] = 'h4c1n1'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'dentist'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD

        profile_response = signup_form2.submit().follow()
        
        # should be on the welcome page
        profile_response.mustcontain("Bienvenue!")
        profile_response.mustcontain("Comment naviguer sur le site")

        # now log out
        self.logout_provider()

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        login_page = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect").follow()

        # should be redirected to the login page
        login_page.mustcontain(u"Connexion")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = 'mctest@veosan.com'
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        
        # response after login is a redirect, so follow
        login_profile_page = login_redirect_response.follow()
        
        # should be back on providers page, logged in and with connection requested message
        
        login_profile_page.mustcontain('mctest@veosan.com')
        login_profile_page.mustcontain("Connection requested")
        login_profile_page.mustcontain('first last')

        
        
        
        
        # logout and log back in as first guy
        self.logout_provider()
        
        login_page = self.testapp.get('/login')
        
        login_page.mustcontain(u"Connexion")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain(self._TEST_PROVIDER_EMAIL)
        login_welcome_page.mustcontain("Bienvenue!")
        login_welcome_page.mustcontain("Comment naviguer sur le site")        
        
        # network page
        network_page = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)
        
        network_page.mustcontain("Here are your pending invitations. Please confirm you know this person.")
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain("Connect")
        network_page.mustcontain("Reject")
        
        # accept the connection
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        accept_link = '/provider/network/' + self._TEST_PROVIDER_VANITY_URL + '/accept/' + source_provider.key.urlsafe()
        network_page = self.testapp.get(accept_link)
        
        network_page.mustcontain("You are now connected to %s %s" % ('david', 'mctester'))
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        
        login_page = self.testapp.get('/login')
        
        login_page.mustcontain(u"Connexion")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = 'mctest@veosan.com'
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain('mctest@veosan.com')
        login_welcome_page.mustcontain("Bienvenue!")
        login_welcome_page.mustcontain("Comment naviguer sur le site")        
        
        network_page = self.testapp.get('/provider/network/' + 'davidmctester')
        
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("first last")
        network_page.mustcontain("Ostéopathe")
        
        
    def test_invite_to_connect_from_profile_accepted(self):
        # create a provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.logout_provider()
        
        # and another
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'david'
        signup_form['last_name'] = 'mctester'
        signup_form['email'] = 'mctest@veosan.com'
        signup_form['postal_code'] = 'h4c1n1'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'dentist'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD

        profile_response = signup_form2.submit().follow()
        
        # should be on the welcome page
        profile_response.mustcontain("Bienvenue!")
        profile_response.mustcontain("Comment naviguer sur le site")

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        
        login_page = self.testapp.get('/login')
        
        login_page.mustcontain(u"Connexion")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain(self._TEST_PROVIDER_EMAIL)
        login_welcome_page.mustcontain("Bienvenue!")
        login_welcome_page.mustcontain("Comment naviguer sur le site")        
        
        # network page
        network_page = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)
        
        network_page.mustcontain("Here are your pending invitations. Please confirm you know this person.")
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain("Connect")
        network_page.mustcontain("Reject")
        
        # accept the connection
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        accept_link = '/provider/network/' + self._TEST_PROVIDER_VANITY_URL + '/accept/' + source_provider.key.urlsafe()
        network_page = self.testapp.get(accept_link)
        
        network_page.mustcontain("You are now connected to %s %s" % ('david', 'mctester'))
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        
        login_page = self.testapp.get('/login')
        
        login_page.mustcontain(u"Connexion")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = 'mctest@veosan.com'
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain('mctest@veosan.com')
        login_welcome_page.mustcontain("Bienvenue!")
        login_welcome_page.mustcontain("Comment naviguer sur le site")        
        
        network_page = self.testapp.get('/provider/network/' + 'davidmctester')
        
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("first last")
        network_page.mustcontain("Ostéopathe")
        
    def test_invite_to_connect_rejected(self):
        # create a provider
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        self.logout_provider()
        
        # and another
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'david'
        signup_form['last_name'] = 'mctester'
        signup_form['email'] = 'mctest@veosan.com'
        signup_form['postal_code'] = 'h4c1n1'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'dentist'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD

        profile_response = signup_form2.submit().follow()
        
        # should be on the welcome page
        profile_response.mustcontain("Bienvenue!")
        profile_response.mustcontain("Comment naviguer sur le site")

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        
        login_page = self.testapp.get('/login')
        
        login_page.mustcontain(u"Connexion")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain(self._TEST_PROVIDER_EMAIL)
        login_welcome_page.mustcontain("Bienvenue!")
        login_welcome_page.mustcontain("Comment naviguer sur le site")        
        
        # network page
        network_page = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)
        
        network_page.mustcontain("Here are your pending invitations. Please confirm you know this person.")
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain("Connect")
        network_page.mustcontain("Reject")
        
        # accept the connection
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        reject_link = '/provider/network/' + self._TEST_PROVIDER_VANITY_URL + '/reject/' + source_provider.key.urlsafe()
        network_page = self.testapp.get(reject_link)
        
        network_page.mustcontain("You have rejected %s %s" % ('david', 'mctester'))
        network_page.mustcontain('Votre réseau est vide!')
        network_page.mustcontain(no="Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it's not on the other side
        self.logout_provider()
        
        login_page = self.testapp.get('/login')
        
        login_page.mustcontain(u"Connexion")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = 'mctest@veosan.com'
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain('mctest@veosan.com')
        login_welcome_page.mustcontain("Bienvenue!")
        login_welcome_page.mustcontain("Comment naviguer sur le site")        
        
        network_page = self.testapp.get('/provider/network/' + 'davidmctester')
        
        network_page.mustcontain('Votre réseau est vide!')



    def test_no_connection_to_self(self):
        pass

    def test_dupe_connections(self):
        pass

    def test_show_connected_after_connect(self):
        pass
    
    def test_display_connections_on_public_profile(self):
        pass


if __name__ == "__main__":
    unittest.main()
    
    
