# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
import logging
from data import db
import testutil
from datetime import datetime
from utilities import time
from babel.dates import format_date, format_datetime, format_time

class PublicProfileTest(BaseTest):
    
    def test_visit_public_profile(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: public view")

    def test_visit_public_profile_self_view(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        self.login_as_provider()

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: self-view")

    def test_visit_public_profile_admin_view(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        self.login_as_admin()

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: public view", admin=True)


    def test_visit_public_profile_from_another_loggedin_provider(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")


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
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        
        # should be on the welcome page
        profile_response.mustcontain("Bienvenue!")
        profile_response.mustcontain("Comment naviguer sur le site")

        # revist first guy's public page
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)

        # check the menu items
        public_profile.mustcontain('mctest@veosan.com')
        public_profile.mustcontain('/provider/profile/davidmctester')
        public_profile.mustcontain('/provider/address/davidmctester')
        public_profile.mustcontain('/provider/welcome/davidmctester')


    def test_disable_enable_show_address(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # hide last name
        public_profile.mustcontain("Fantastic Fox")
                
        public_profile.mustcontain(no="Map")
        public_profile.mustcontain(no="Réservez Maintenant")
        
        # enable the address
        self.login_as_admin()
        enable = self.testapp.post('/admin/provider/feature/address_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Map")
        
        
        # hit it again to disable the address
        disable = self.testapp.post('/admin/provider/feature/address_enabled/' + self._TEST_PROVIDER_VANITY_URL)

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        
    def test_disable_enable_show_booking(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        
        self.login_as_admin()
        
        public_profile.mustcontain(no="Map")

        
        # enable the booking
        enable = self.testapp.post('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Réservez Maintenant")
        
        
        # hit it again to disable the booking
        disable = self.testapp.post('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Réservez Maintenant")
        
        
    def test_book_from_public_profile_new_patient(self):
        date_string = testutil.next_monday_date_string()
        time_string = '10'
        self.book_from_public_profile(date_string, time_string)

        # check provider bookings list, should be empty as booking is not confirmed  
        # switch to french
        repsonse = self.testapp.get('/lang/fr')

        self.login_as_provider()
        provider_bookings = self.testapp.get('/provider/bookings/' + self._TEST_PROVIDER_VANITY_URL)
        provider_bookings.mustcontain('Vous n’avez aucun rendez-vous prévu')
        self.logout_provider()
        
        # check patient's booking list
        #self.login_as_patient()
        
        # check datetime
        #self.logout_as_patient()
        
        # check admin side bookings
        self.login_as_admin()
        admin_bookings_page = self.testapp.get('/admin/bookings')
        admin_datetime = testutil.next_monday_date_string() + " 10:00"
        admin_bookings_page.mustcontain(admin_datetime)
        admin_bookings_page.mustcontain('Fantastic Fox')
        admin_bookings_page.mustcontain('Pat Patient')
        admin_bookings_page.mustcontain(self._TEST_PATIENT_TELEPHONE)
        admin_bookings_page.mustcontain(self._TEST_PATIENT_EMAIL)
        admin_bookings_page.mustcontain('Patient not confirmed')
        admin_bookings_page.mustcontain('public profile')
        self.logout_admin()
        
        # check event logs
        
        
        booking_datetime = datetime.strptime(testutil.next_monday_date_string() + " 10", '%Y-%m-%d %H')
        french_datetime_string = format_datetime(booking_datetime, "EEEE 'le' d MMMM yyyy", locale='fr_CA') + " à " + format_datetime(booking_datetime, "H:mm", locale='fr_CA')
        logging.info('French date time of booking: %s' % french_datetime_string) 
        # no email sent to provider (patient is not confirmed)
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(0, len(messages))
        # check that confirmation emails was sent to patient
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        self.assertEqual(self._TEST_PATIENT_EMAIL, m.to)
        
        # activate account
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        
        self.assertEquals(m.subject, 'Rendez-vous Veosan - Ostéopathe')
        #self.assertEqual(m.sender, 'first last <support@veosan.com>')
        #self.assertEqual(m.reply_to, self._TEST_PROVIDER_EMAIL)
        #self.assertIn('Please click on the link below to create your profile', m.body.payload)
        #self.assertIn("I've been using Veosan and thought you might like to try it out. Here's an invitation to create a profile.", m.body.payload)
        user = db.get_user_from_email(self._TEST_PATIENT_EMAIL)
        # check email content
        self.assertTrue('/user/activation/%s' % user.signup_token in m.body.payload)
        self.assertIn('Bonjour', m.body.payload)
        self.assertIn('Merci', m.body.payload)
        # click the link
        confirmation_page = self.testapp.get('/user/activation/%s' % user.signup_token)
        confirmation_page.mustcontain('Votre rendez-vous est confirmé')
        confirmation_page.mustcontain(french_datetime_string)
        confirmation_page.mustcontain("Fantastic Fox")
        # Check email to provider    
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        provider_mail = messages[0]
        self.assertEquals(provider_mail.subject, 'Veosan - Nouveau rendez-vous avec Pat Patient')
        #self.assertEqual(m.sender, 'first last <support@veosan.com>')
        #self.assertEqual(m.reply_to, self._TEST_PROVIDER_EMAIL)
        self.assertIn('Vous avez un nouveau rendez-vous', provider_mail.body.payload)
        self.assertIn("Consultez vos rendez-vous ici", provider_mail.body.payload)

        
        # check status change in all lists (provider, patient and admin dashboards)
       
        self.login_as_provider()
        provider_bookings = self.testapp.get('/provider/bookings/' + self._TEST_PROVIDER_VANITY_URL)
        provider_bookings.mustcontain('Pat Patient')
        # check datetime
        provider_bookings.mustcontain(french_datetime_string)
        self.logout_provider()
        

if __name__ == "__main__":
    unittest.main()
    
    
