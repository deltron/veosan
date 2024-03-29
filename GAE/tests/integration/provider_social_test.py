# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderSocialTest(BaseTest):
    def test_invite_provider(self):
        self.self_signup_provider()
        
        response = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)

        invite_provider_form = response.forms['invite_provider_form']
        invite_provider_form['first_name'] = 'david'
        invite_provider_form['last_name'] = 'mctest'
        invite_provider_form['email'] = 'mctest@veosan.com'
        
        # default no note
        
        response = invite_provider_form.submit()
        response.mustcontain("Invitation envoyée à david mctest")



        messages = self.mail_stub.get_sent_messages(to='mctest@veosan.com')
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Invitation to join Veosan from %s %s' % ('first', 'last'))
        self.assertEqual(m.sender, 'first last <support@veosan.com>')
        self.assertEqual(m.reply_to, self._TEST_PROVIDER_EMAIL)
        self.assertIn('SVP suivez le lien ci-dessous pour créer votre profil:', m.body.payload)
        self.assertIn("J'utilise Veosan et j'ai pensé que vous aimeriez l'essayer. Voici une invitation pour créer un profil.", m.body.payload)

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

        response2 = signup_form.submit()
        
        signup_form2 = response2.forms['provider_signup_form2']
        signup_form2['category'] = 'dietitian'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

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

    def test_invite_provider_already_a_member(self):
        # signup first provider
        self.self_signup_provider()
        self.logout_provider()

        # create anoter provider
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')
        self.logout_provider()
        
        # log back in as first guy
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        
        # invite the first one (already a member)
        response = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)

        invite_provider_form = response.forms['invite_provider_form']
        invite_provider_form['first_name'] = 'david'
        invite_provider_form['last_name'] = 'mctest'
        invite_provider_form['email'] = 'mctest@veosan.com'
        
        # default no note
        response = invite_provider_form.submit().follow()
        response.mustcontain("Connexion demandée")

        # check email and accept
        messages = self.mail_stub.get_sent_messages(to='mctest@veosan.com')
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Join my network on Veosan!')
        self.assertEqual(m.sender, 'first last <support@veosan.com>')
        self.assertEqual(m.reply_to, self._TEST_PROVIDER_EMAIL)
        
        source_provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        self.assertIn("%s %s veut se connecter avec vous sur Veosan." % (source_provider.first_name, source_provider.last_name), m.body.payload)
        self.assertIn("SVP suivez le lien ci-dessous pour accepter:", m.body.payload)
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        self.assertIn("/login/accept/%s" % lnk, m.body.payload)

        # accept the connection by clicking link in email
        login_page = self.testapp.get('/login/accept/%s' % lnk)
        login_page.mustcontain(u"Connexion")
        
        # email should be pre-populated
        login_page.mustcontain('mctest@veosan.com')

        # fill out details
        login_form = login_page.forms[0]
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()

        # response after login is a redirect, so follow
        network_page = login_redirect_response.follow()
        
        network_page.mustcontain("Vous êtes maintenant connecté à first last")
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("first last")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        
        network_page = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)
        
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("first last")
        network_page.mustcontain("Ostéopathe")
        
        



    def test_invite_token_already_used(self):
        self.self_signup_provider()
        
        response = self.testapp.get('/provider/network/' + self._TEST_PROVIDER_VANITY_URL)

        invite_provider_form = response.forms['invite_provider_form']
        invite_provider_form['first_name'] = 'david'
        invite_provider_form['last_name'] = 'mctest'
        invite_provider_form['email'] = 'mctest@veosan.com'
        
        # default no note
        
        response = invite_provider_form.submit()
        response.mustcontain("Invitation envoyée à david mctest")



        messages = self.mail_stub.get_sent_messages(to='mctest@veosan.com')
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Invitation to join Veosan from %s %s' % ('first', 'last'))
        self.assertEqual(m.sender, 'first last <support@veosan.com>')
        self.assertEqual(m.reply_to, self._TEST_PROVIDER_EMAIL)
        self.assertIn('SVP suivez le lien ci-dessous pour créer votre profil:', m.body.payload)
        self.assertIn("J'utilise Veosan et j'ai pensé que vous aimeriez l'essayer. Voici une invitation pour créer un profil.", m.body.payload)

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

        response2 = signup_form.submit()
        
        signup_form2 = response2.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

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
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now log out
        self.logout_provider()

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        login_page = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect").follow()

        # should be redirected to the login page
        login_page.mustcontain(u"Login")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = 'mctest@veosan.com'
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        
        # response after login is a redirect, so follow
        login_profile_page = login_redirect_response.follow()
        
        # should be back on providers page, logged in and with connection requested message
        
        login_profile_page.mustcontain('mctest@veosan.com')
        login_profile_page.mustcontain("Connexion demandée")
        login_profile_page.mustcontain('first last')

        # logout and log back in as first guy
        self.logout_provider()
        
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)


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
        
        network_page.mustcontain('Vous êtes maintenant connecté à david mctester')
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        
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
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)

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
        
        network_page.mustcontain("Vous êtes maintenant connecté à david mctester")
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)


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
        profile_page.mustcontain("Vous êtes connecté avec david!")
    
    def test_invite_to_connect_rejected(self):
        # create a provider
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        

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
        
        network_page.mustcontain("Vous avez rejeté david mctester")
        network_page.mustcontain('Votre réseau est vide!')
        
        network_page.mustcontain(no="Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it's not on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        

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
        

    def test_invite_to_connect_accept_from_email_not_logged_in(self):
        # create a provider
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

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
        
        self.assertIn("%s %s veut se connecter avec vous sur Veosan." % (source_provider.first_name, source_provider.last_name), m.body.payload)
        self.assertIn("SVP suivez le lien ci-dessous pour accepter:", m.body.payload)
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        self.assertIn("/login/accept/%s" % lnk, m.body.payload)

        # accept the connection by clicking link in email
        login_page = self.testapp.get('/login/accept/%s' % lnk)
        
        is_french = 'Connexion' in login_page
        is_english = 'Login' in login_page

        if is_english:
            login_page.mustcontain(u"Login")
        elif is_french:
            login_page.mustcontain(u"Connexion")

        
        # email should be pre-populated
        login_page.mustcontain(self._TEST_PROVIDER_EMAIL)

        # fill out details
        login_form = login_page.forms[0]
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()

        # response after login is a redirect, so follow
        network_page = login_redirect_response.follow()
        
        if is_english:
            network_page.mustcontain("Vous êtes maintenant connecté à david mctester")
            network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
            network_page.mustcontain("david mctester")
            network_page.mustcontain("Dentiste")
            network_page.mustcontain(no="Connect")
            network_page.mustcontain(no="Reject")
            network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")
        
        elif is_french:
            network_page.mustcontain("Vous êtes maintenant connecté à david mctester")
            network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
            network_page.mustcontain("david mctester")
            network_page.mustcontain("Dentiste")
            network_page.mustcontain(no="Connect")
            network_page.mustcontain(no="Reject")
            network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        
        network_page = self.testapp.get('/provider/network/' + 'davidmctester')
        
        if is_english:
            network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
            network_page.mustcontain("first last")
            network_page.mustcontain("Ostéopathe")
        elif is_french:
            network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
            network_page.mustcontain("first last")
            network_page.mustcontain("Ostéopathe")
        

    def test_connect_while_pending(self):
        # this would create a duplicate connection, should give a message
        
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # now should be pending...but what if we click connect again
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        response.mustcontain("Connexion en attente")
        
        # make sure only 1 email was sent, don't want to be a spambot!
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Join my network on Veosan!')
        self.assertEqual(m.sender, 'david mctester <support@veosan.com>')
        self.assertEqual(m.reply_to, 'mctest@veosan.com')
        
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        self.assertIn("%s %s veut se connecter avec vous sur Veosan." % (source_provider.first_name, source_provider.last_name), m.body.payload)
        self.assertIn("SVP suivez le lien ci-dessous pour accepter:", m.body.payload)
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        self.assertIn("/login/accept/%s" % lnk, m.body.payload)
        
        # login as target, make sure only 1 pending request

        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        

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
        self.self_signup_provider()
        self.logout_provider()

        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)

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
        
        network_page.mustcontain("Vous êtes maintenant connecté à david mctester")
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)

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
        login_page.mustcontain(u"Login")
        # fill out details
        login_form = login_page.forms[0]
        login_form['email'] = 'mctest@veosan.com'
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()
        
        # response after login is a redirect, so follow
        login_profile_page = login_redirect_response.follow()
        
        # should be back on providers page, logged in and with connection requested message
        
        login_profile_page.mustcontain('mctest@veosan.com')
        login_profile_page.mustcontain("Vous êtes déjà connecté")
        login_profile_page.mustcontain('first last')
        

    def test_no_message_no_button_on_self_profile(self):
        self.self_signup_provider()

        # turn on connect buttons
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        provider.connect_enabled = True
        provider.put()
        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no='/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        response.mustcontain("first est relié à 0 professionels de la santé.")
        response.mustcontain("Voir toutes les connections")

    def test_no_connection_to_self(self):
        self.self_signup_provider()

        # force connect with URL
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/connect')
        response.mustcontain("Vous ne pouvez pas vous connecter à vous-même!")
        
        # check database
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEquals(0, provider.get_provider_network_count())
        self.assertEquals(0, provider.get_provider_network_pending_count())



    def test_dupe_connections(self):
        # actually force it through with the URL
        self.self_signup_provider()
        self.logout_provider()

        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)

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
        
        network_page.mustcontain('Vous êtes maintenant connecté à david mctester')
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        
        network_page = self.testapp.get('/provider/network/' + 'davidmctester')
        
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("first last")
        network_page.mustcontain("Ostéopathe")
                
        
        # force connect with URL
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no='/' + self._TEST_PROVIDER_VANITY_URL + '/connect')

        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/connect')
        response.mustcontain("Vous êtes déjà connecté!")
        
        # check database
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertEquals(1, provider.get_provider_network_count())
        self.assertEquals(0, provider.get_provider_network_pending_count())


    def test_click_accept_from_email_already_logged_in(self):
        # actually force it through with the URL
        self.self_signup_provider()
        self.logout_provider()

        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        
        #check messages
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Join my network on Veosan!')
        self.assertEqual(m.sender, 'david mctester <support@veosan.com>')
        self.assertEqual(m.reply_to, 'mctest@veosan.com')
        
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        self.assertIn("%s %s veut se connecter avec vous sur Veosan." % (source_provider.first_name, source_provider.last_name), m.body.payload)
        self.assertIn("SVP suivez le lien ci-dessous pour accepter:", m.body.payload)
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        self.assertIn("/login/accept/%s" % lnk, m.body.payload)

        # accept the connection by clicking link in email
        accept_page = self.testapp.get('/login/accept/%s' % lnk).follow()
                
        # already logged in, just go straight to the point
        accept_page.mustcontain(no="Connexion")
        
        accept_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        accept_page.mustcontain("david mctester")
        accept_page.mustcontain("Dentiste")
        accept_page.mustcontain("Vous êtes maintenant connecté à david mctester")

    def test_invite_reject_invite_again_accept(self):
        # create a provider
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        response.mustcontain('Connexion demandée')
        
        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        

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
        
        network_page.mustcontain("Vous avez rejeté david mctester")
        network_page.mustcontain('Votre réseau est vide!')
        
        network_page.mustcontain(no="Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it's not on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        

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
        
        
        # now invite again
        self.logout_provider()   
        
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        
        
        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        
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
        
        network_page.mustcontain('Vous êtes maintenant connecté à david mctester')
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)


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
        profile_page.mustcontain('Vous êtes connecté avec david!')
        
        #check rejection count
        provider_source = db.get_provider_from_email('mctest@veosan.com')
        provider_target = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)

        provider_network_connection = db.get_provider_network_connection(provider_source.key, provider_target.key)
        self.assertEqual(provider_network_connection.rejection_count, 1)
    
    
    def test_invite_reject_invite_again_reject_again(self):
        # create a provider
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        response.mustcontain('Connexion demandée')
        
        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        

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
        
        network_page.mustcontain('Vous avez rejeté david mctester')
        network_page.mustcontain('Votre réseau est vide!')
        
        network_page.mustcontain(no="Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it's not on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        

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
        
        
        # now invite again
        self.logout_provider()   
        
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        
        
        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")

        # logout and log back in as first guy
        self.logout_provider()
        self.login_as_provider(email=self._TEST_PROVIDER_EMAIL, password=self._TEST_PROVIDER_PASSWORD)
        
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
        
        network_page.mustcontain('Vous avez rejeté david mctester')
        network_page.mustcontain('Votre réseau est vide!')
        
        network_page.mustcontain(no="Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it's not on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        

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

        #check rejection count
        provider_source = db.get_provider_from_email('mctest@veosan.com')
        provider_target = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)

        provider_network_connection = db.get_provider_network_connection(provider_source.key, provider_target.key)
        self.assertEqual(provider_network_connection.rejection_count, 2)
    


    def test_accept_invite_from_email_already_logged_in_as_inviter(self):
        # create a provider
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')

        # now go to the first guy's profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # click connect
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + "/connect")
        response.mustcontain('Connexion demandée')
                
        # now check email and click accept (while logged in as 2nd guy)
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        self.assertEqual(m.subject, 'Join my network on Veosan!')
        self.assertEqual(m.sender, 'david mctester <support@veosan.com>')
        self.assertEqual(m.reply_to, 'mctest@veosan.com')
        
        source_provider = db.get_provider_from_email('mctest@veosan.com')
        
        self.assertIn("%s %s veut se connecter avec vous sur Veosan." % (source_provider.first_name, source_provider.last_name), m.body.payload)
        self.assertIn("SVP suivez le lien ci-dessous pour accepter:", m.body.payload)
        
        lnk = source_provider.get_provider_network_pending_connections_source()[0].key.urlsafe()

        self.assertIn("/login/accept/%s" % lnk, m.body.payload)

        # accept the connection by clicking link in email
        login_page = self.testapp.get('/login/accept/%s' % lnk)

        # this should log out the 2nd provider and prompt the first one to login
        login_page.mustcontain(u"Connexion")
        
        # email should be pre-populated
        login_page.mustcontain(self._TEST_PROVIDER_EMAIL)

        # fill out details
        login_form = login_page.forms[0]
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect_response = login_form.submit()

        # response after login is a redirect, so follow
        network_page = login_redirect_response.follow()
        
        network_page.mustcontain("Vous êtes maintenant connecté à david mctester")
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentiste")
        network_page.mustcontain(no="Connect")
        network_page.mustcontain(no="Reject")
        network_page.mustcontain(no="Here are your pending invitations. Please confirm you know this person.")

        # now check it shows up on the other side
        self.logout_provider()
        self.login_as_provider(email='mctest@veosan.com', password=self._TEST_PROVIDER_PASSWORD)
        
        network_page = self.testapp.get('/provider/network/' + 'davidmctester')
        
        network_page.mustcontain('Votre réseau contient 1 professionels de la santé.')
        network_page.mustcontain("first last")
        network_page.mustcontain("Ostéopathe")
              
    def test_force_connection_by_admin(self):
        # create a provider
        self.self_signup_provider()
        self.logout_provider()
        
        # and another
        self.self_signup_provider(email='mctest@veosan.com', first_name='david', last_name='mctester', category='dentist')
        self.logout_provider()
        
        # now force friend connect
        self.login_as_admin()
        
        provider_admin_page = self.testapp.get('/admin/provider/admin/' + 'davidmctester')
        force_connect_form = provider_admin_page.forms['force_friends']
        force_connect_form['email'] = self._TEST_PROVIDER_EMAIL
        force_connect_form.submit()
        
        self.logout_admin()
        
        network_page = self.testapp.get('/' + 'davidmctester')
        
        network_page.mustcontain('david est relié à 1 professionels de la santé.')
        network_page.mustcontain("first last")
        network_page.mustcontain("Ostéopathe")
        
        network_page = self.testapp.get('/' + 'firstlast')
        
        network_page.mustcontain('first est relié à 1 professionels de la santé.')
        network_page.mustcontain("david mctester")
        network_page.mustcontain("Dentist")

if __name__ == "__main__":
    unittest.main()
    
    
