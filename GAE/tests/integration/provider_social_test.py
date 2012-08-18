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
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        accept_link = '/provider/network/' + self._TEST_PROVIDER_VANITY_URL + '/accept/' + lnk
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
        
        # turn on connect buttons & public profile
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        provider.connect_enabled = True
        provider.put()        
        
        provider = db.get_provider_from_email('mctest@veosan.com')
        provider.connect_enabled = True
        provider.put()        
        
        # check it shows up on public profile
        profile_page = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        profile_page.mustcontain(no='/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        profile_page.mustcontain("david mctester")
        profile_page.mustcontain("Dentiste")
        profile_page.mustcontain("first est relié à 1 professionels de la santé.")
        
        profile_page = self.testapp.get('/davidmctester')
        profile_page.mustcontain(no='/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        profile_page.mustcontain("first last")
        profile_page.mustcontain("Ostéopathe")
        profile_page.mustcontain("david est relié à 1 professionels de la santé.")
        
        
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
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        accept_link = '/provider/network/' + self._TEST_PROVIDER_VANITY_URL + '/accept/' + lnk
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

        # turn on connect buttons & public profile
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        provider.connect_enabled = True
        provider.put()        
        
        provider = db.get_provider_from_email('mctest@veosan.com')
        provider.connect_enabled = True
        provider.put()        
        
        # check it shows up on public profile
        profile_page = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        profile_page.mustcontain(no='/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        profile_page.mustcontain("david mctester")
        profile_page.mustcontain("Dentiste")
        profile_page.mustcontain("first est relié à 1 professionels de la santé.")
        
        profile_page = self.testapp.get('/davidmctester')
        profile_page.mustcontain(no='/davidmctester/connect')
        profile_page.mustcontain("first last")
        profile_page.mustcontain("Ostéopathe")
        profile_page.mustcontain("david est relié à 1 professionels de la santé.")
        
        self.login_as_provider()
        profile_page = self.testapp.get('/davidmctester')
        profile_page.mustcontain("You and david are connected!")
    
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
        
        # reject the connection
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        reject_link = '/provider/network/' + self._TEST_PROVIDER_VANITY_URL + '/reject/' + lnk
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

        self.logout_provider()

        # turn on connect buttons & public profile
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        provider.connect_enabled = True
        provider.put()        
        
        provider = db.get_provider_from_email('mctest@veosan.com')
        provider.connect_enabled = True
        provider.put()        
        
        # check it doest not shows up on public profile
        profile_page = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        profile_page.mustcontain('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        profile_page.mustcontain(no="david mctester")
        profile_page.mustcontain(no="Dentiste")
        profile_page.mustcontain("first est relié à 0 professionels de la santé.")
        
        profile_page = self.testapp.get('/davidmctester')
        profile_page.mustcontain('/davidmctester/connect')
        profile_page.mustcontain(no="first last")
        profile_page.mustcontain(no="Ostéopathe")
        profile_page.mustcontain("david est relié à 0 professionels de la santé.")
        

    def test_invite_to_connect_accept_from_email(self):
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

        # logout and check email
        self.logout_provider()

        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Join my network on Veosan!')
        self.assertEqual(m.sender, 'david mctester <support@veosan.com>')
        self.assertEqual(m.reply_to, 'mctest@veosan.com')
        
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        self.assertIn("%s %s wants to connect with you on Veosan." % (source_provider.first_name, source_provider.last_name), m.body.payload)
        self.assertIn("Please click the following link to accept :", m.body.payload)
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        self.assertIn("/login/accept/%s" % lnk, m.body.payload)

        # accept the connection by clicking link in email
        login_page = self.testapp.get('/login/accept/%s' % lnk)
        login_page.mustcontain(u"Connexion")
        
        # email should be pre-populated
        login_page.mustcontain(self._TEST_PROVIDER_EMAIL)

        # fill out details
        login_form = login_page.forms[0]
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()

        # response after login is a redirect, so follow
        network_page = login_redirect_response.follow()
        
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
        

    def test_connect_while_pending(self):
        # this would create a duplicate connection, should give a message
        
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

        # now should be pending...but what if we click connect again
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        response.mustcontain("Connection pending")
        
        # make sure only 1 email was sent, don't want to be a spambot!
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Join my network on Veosan!')
        self.assertEqual(m.sender, 'david mctester <support@veosan.com>')
        self.assertEqual(m.reply_to, 'mctest@veosan.com')
        
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        self.assertIn("%s %s wants to connect with you on Veosan." % (source_provider.first_name, source_provider.last_name), m.body.payload)
        self.assertIn("Please click the following link to accept :", m.body.payload)
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        self.assertIn("/login/accept/%s" % lnk, m.body.payload)
        
        # login as target, make sure only 1 pending request

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
        
  
    def test_connect_logout_connect_again_from_profile(self):
        # this would create a duplicate connection, should give a message
        # "You are already connected" after login
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
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()
        
        accept_link = '/provider/network/' + self._TEST_PROVIDER_VANITY_URL + '/accept/' + lnk
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
        
        # now logout
        self.logout_provider()
        
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
        login_profile_page.mustcontain("Already connected")
        login_profile_page.mustcontain('first last')
        

    def test_no_message_no_button_on_self_profile(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        # turn on connect buttons
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        provider.connect_enabled = True
        provider.put()
        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no='/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        response.mustcontain("first est relié à 0 professionels de la santé.")
        response.mustcontain("Voir toutes les connections")

    def test_no_connection_to_self(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        # force connect with URL
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/connect')
        response.mustcontain("You can't connect to yourself!")
        
        # check database
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEquals(0, provider.get_provider_network_count())
        self.assertEquals(0, provider.get_provider_network_pending_count())



    def test_dupe_connections(self):
        # actually force it through with the URL
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
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        accept_link = '/provider/network/' + self._TEST_PROVIDER_VANITY_URL + '/accept/' + lnk
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
                
        
        # force connect with URL
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no='/' + self._TEST_PROVIDER_VANITY_URL + '/connect')

        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/connect')
        response.mustcontain("Already connected!")
        
        # check database
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEquals(1, provider.get_provider_network_count())
        self.assertEquals(0, provider.get_provider_network_pending_count())


    def test_click_accept_from_email_already_logged_in(self):
        # actually force it through with the URL
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
        
        #check messages
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Join my network on Veosan!')
        self.assertEqual(m.sender, 'david mctester <support@veosan.com>')
        self.assertEqual(m.reply_to, 'mctest@veosan.com')
        
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        self.assertIn("%s %s wants to connect with you on Veosan." % (source_provider.first_name, source_provider.last_name), m.body.payload)
        self.assertIn("Please click the following link to accept :", m.body.payload)
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        self.assertIn("/login/accept/%s" % lnk, m.body.payload)

        # accept the connection by clicking link in email
        accept_page = self.testapp.get('/login/accept/%s' % lnk).follow()
                
        # already logged in, just go straight to the point
        accept_page.mustcontain(no="Connexion")
        
        accept_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        accept_page.mustcontain("david mctester")
        accept_page.mustcontain("Dentiste")
        accept_page.mustcontain("You are now connected to david mctester")

if __name__ == "__main__":
    unittest.main()
    
    
