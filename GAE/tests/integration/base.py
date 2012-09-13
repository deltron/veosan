# -*- coding: utf-8 -*-

from google.appengine.ext import testbed
import os, logging
import unittest, webtest
from StringIO import StringIO
from babel.dates import format_datetime, format_time
from babel.dates import format_date

# veo
import main
import data.db as db
from handler import auth
from data.model import Patient
from datetime import datetime
from data.model import User, Booking
import util, testutil
from google.appengine.datastore import datastore_stub_util
from webapp2_extras import i18n
import utilities

class BaseTest(unittest.TestCase):
    util.BOOKING_ENABLED = True
    
    ''' *** NOTE ***
    
    Settings in app.yaml are ignored by tests
    App assumes login is "magically" handled properly
    
    '''    
       
    _TEST_PROVIDER_EMAIL = "unit_test@provider.com"
    _TEST_PROVIDER_TELEPHONE = '514-999-0987'
    _TEST_PROVIDER_PASSWORD = u'123456'

    _TEST_ADMIN_EMAIL = "unit_test@admin.com"

    _TEST_PATIENT_EMAIL = 'pat@patient.com'
    _TEST_PATIENT_PASSWORD = '654321'
    _TEST_PATIENT_TELEPHONE = '514-123-1234'
    
    _TEST_PROVIDER_VANITY_URL = 'firstlast'

    def setUp(self):
        # Wrap the app with WebTest’s TestApp.
        self.testapp = webtest.TestApp(main.application)
        
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        self.testbed.init_blobstore_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        #self.testbed.init_search_stub()
        # mail stubs
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        # set up the logger
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        # en francais


    def tearDown(self):
        self.testbed.deactivate()
        
        # close down the logger
        self.handler.flush()
        self.log.removeHandler(self.handler)
        self.handler.close()


    def assert_msg_in_log(self, msg, admin=False):
        events = db.get_events_all()
        log_present = False
        try:
            # usual case is there is > 1 result
            log_present = any((msg in event.description and event.admin == admin) for event in events)
        except TypeError:
            # if there is only one, check it
            log_present = msg in events.description and events.admin == admin
        
        self.assertTrue(log_present, "Event log message missing: %s, admin=%s" % (msg, admin))


    
    ##
    ## Testbed Authentication methods
    ##
    
    def login_as_admin(self):
        self.set_current_google_user('admin@veosan.com', 'admin@veosan.com', is_admin=True)
    
    def logout_admin(self):
        if os.environ.has_key('USER_EMAIL'):
            del os.environ['USER_EMAIL']
        
        if os.environ.has_key('USER_ID'):
            del os.environ['USER_ID']
        
        if os.environ.has_key('USER_IS_ADMIN'):
            del os.environ['USER_IS_ADMIN']
        
    def set_current_google_user(self, email, user_id, is_admin=False):    
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'
        
        
    def login_as_provider(self, email=_TEST_PROVIDER_EMAIL, password=_TEST_PROVIDER_PASSWORD):
        ''' login as a provider, assumes already initialized and accepted terms '''
        login_page = self.testapp.get('/login')
        
        login_page.mustcontain(u"Connexion")
        login_form = login_page.forms[0]
        login_form['email'] = email
        login_form['password'] = password
        login_redirect = login_form.submit()
        response = login_redirect.follow()
        
        # default page for provider after login is welcome
        response.mustcontain("Profil")
        response.mustcontain(email)
        response.mustcontain("Bienvenue!")
        response.mustcontain("Comment naviguer sur le site")        

        # check the event log
        #self.assert_msg_in_log("Provider Logged In")

        return response
        

    def logout_provider(self, language = None):
        logout_redirect = self.testapp.get('/logout')
        logout_response = logout_redirect.follow()
        
        if language is 'en':
            logout_response.mustcontain('My Account')
        else:
            logout_response.mustcontain('Mon Compte')
        
    
    def login_as_patient(self):
        # switch to french
        repsonse = self.testapp.get('/lang/fr')
        
        response = self.testapp.get('/login')
        response.mustcontain(u"Connexion")

        login_form = response.forms[0]
        login_form['email'] = self._TEST_PATIENT_EMAIL
        login_form['password'] = self._TEST_PATIENT_PASSWORD
        login_redirect_response = login_form.submit()
        # response after login is a redirect, so follow        
        login_welcome_page = login_redirect_response.follow()
        # email in the header
        login_welcome_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # login lands on index page
        login_welcome_page.mustcontain('Rendez-vous à venir')
        
        
    def logout_patient(self):
        logout_redirect = self.testapp.get('/logout')
        logout_response = logout_redirect.follow()
        logout_response.mustcontain('Mon Compte')
        
        
    ######################################################################
    ## PROVIDER AND ADMIN METHODS
    ######################################################################
    
    def create_complete_provider_profile_selfserve(self):
        self.self_signup_provider()
    
    def create_complete_provider_profile(self):
        '''
            Test init provider with address, profile and one timeslot together.
            
            There is one timeslot available (Monday at 9am)
        '''
        self.self_signup_provider()
        
        # fill all sections
        self.fill_new_provider_address_correctly_action()
        self.fill_new_provider_profile_correctly_action()
        self.provider_schedule_set_one_timeslot_action()

        # logout
        self.logout_provider()
        

    def self_signup_provider(self, email=_TEST_PROVIDER_EMAIL, first_name='first', last_name='last', category='osteopath'):
        # switch to french
        response = self.testapp.get('/fr/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = first_name
        signup_form['last_name'] = last_name
        signup_form['email'] = email
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = category
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['terms_agreement'] = 'True'

        profile_response = signup_form2.submit().follow()
        
        # should be on the welcome page
        profile_response.mustcontain("Bienvenue!")
        profile_response.mustcontain("Comment naviguer sur le site")
                
        
    def fill_new_provider_address_correctly_action(self):
        # request the address page
        response = self.testapp.get('/provider/address/%s' % self._TEST_PROVIDER_VANITY_URL)
        #response.showbrowser()
        address_form = response.forms['address_form'] # address form
        
        # fill out the form
        address_form['title'] = u"mr"
        address_form['first_name'] = u"Fantastic"
        address_form['last_name'] = u"Fox"
        address_form['phone'] = self._TEST_PROVIDER_TELEPHONE
        address_form['address'] = u"123 Main St."
        address_form['city'] = u"Westmount"
        address_form['postal_code'] = u"H1B2C3"

        
        # submit it
        response = address_form.submit()
        response.mustcontain("Vos modifications ont été enregistrées.")

        # check values in database
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # iterate over every field item, find the match in the provider object and check its equality
        # possible we miss something here?
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # go back to the admin page, check the name is updated
        self.login_as_admin()
        response = self.testapp.get('/admin/providers')
        response.mustcontain("Fox")
        response.mustcontain("unit_test@provider.com")
        self.logout_admin()
        
        # check the event log
        #self.assert_msg_in_log("Edit Address: Success", admin=False)

    def modify_provider_address_action(self):        
        # request the address page
        response = self.testapp.get('/provider/address/%s' % self._TEST_PROVIDER_VANITY_URL)
        
        address_form = response.forms[0] # address form
        
        # verify form contains correct info
        self.assertEqual(address_form['title'].value, u"mr")
        self.assertEqual(address_form['first_name'].value, u"Fantastic")
        self.assertEqual(address_form['last_name'].value, u"Fox")
        self.assertEqual(address_form['phone'].value, self._TEST_PROVIDER_TELEPHONE)
        self.assertEqual(address_form['address'].value, u"123 Main St.")
        self.assertEqual(address_form['city'].value, u"Westmount")
        self.assertEqual(address_form['postal_code'].value, u"H1B2C3")

        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # iterate over every field item, find the match in the provider object and check its equality
        # with database
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # make some changes to the form
        address_form['title'] = u"mrs"
        address_form['first_name'] = u"Linda"
        address_form['last_name'] = u"Otter"
        address_form['phone'] = u"555-987-6543"
        address_form['address'] = u"321 Primary St."
        address_form['city'] = u"Outremont"
        address_form['postal_code'] = u"C4B5C6"


        # submit it
        response = address_form.submit()
        response.mustcontain("Vos modifications ont été enregistrées.")

        # check values in database
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # iterate over every field item, find the match in the provider object and check its equality
        # possible we miss something here?
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # go back to the admin page, check the name is updated
        self.login_as_admin()
        response = self.testapp.get('/admin/providers')
        response.mustcontain("Otter")
        response.mustcontain("Linda")
        response.mustcontain("unit_test@provider.com")

        # check the event log
        #self.assert_msg_in_log("Edit Address: Success", admin=True)

        
    def fill_new_provider_profile_correctly_action(self, as_admin=True):
        
        # request the address page
        response = self.testapp.get('/provider/profile/%s' % self._TEST_PROVIDER_VANITY_URL)
         
        profile_form = response.forms[0] # address form
        
        # fill out the form        
        profile_form.set('practice_sites', True, 0) # onsite visits


        profile_form['bio'] = "Areas of interest include treatment and management of spinal conditions with an emphasis on manual therapy and rehabilitative exercise."        
        profile_form['quote'] = "The quick brown fox jumped over the lazy dog."

        # submit it
        response = profile_form.submit()
        
        # go back to the profile page
        
        response = self.testapp.get('/provider/profile/%s' % self._TEST_PROVIDER_VANITY_URL)

        response.mustcontain("Areas of interest include treatment and management")
        response.mustcontain("The quick brown fox jumped over the lazy dog")

        # TODO - switch to Beautiful Soup to parse HTML?
        response.mustcontain('input checked id="practice_sites-0" name="practice_sites" type="checkbox" value="onsite"')        
        
        # check values in database
        provider = db.get_provider_from_email("unit_test@provider.com")
        
        # iterate over every field item, find the match in the provider object and check its equality
        # possible we miss something here?
        for k in iter(profile_form.fields):
            if hasattr(provider, str(k)):
                value = getattr(provider, k)
                if isinstance(value, str):
                    self.assertEquals(profile_form[k].value, value)
                #elif isinstance(value, list):   
                    # TODO: how to check this automatically?
                    #self.assertIn(profile_form[k].values, value)
        
                
        self.assertIn('onsite', provider.practice_sites)

        # check the event log
        #self.assert_msg_in_log("Edit Profile: Success", admin=as_admin)


    def provider_schedule_set_one_timeslot_action(self, day='monday', start_time=9, end_time=12):

        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # request the schedule page
        response = self.testapp.get('/provider/schedule/%s' % provider.vanity_url)
        
        # Check that schedule is empty

        # Add an available schedule Monday morning 9-12
        response = self.testapp.get('/provider/schedule/%s/add/%s/%s' % (provider.vanity_url, day, start_time))
        
        schedule_form = response.forms['schedule_form']
        
        # check the form selects are filled with values
        
        schedule_form['day'] = day
        schedule_form['start_time'] = start_time
        schedule_form['end_time'] = end_time
        response = schedule_form.submit().follow()
        
        provider = db.get_provider_from_email("unit_test@provider.com")
        
        # check one schedule was saved in the database
        schedule_count = provider.get_schedules().count()
        self.assertGreater(schedule_count , 0, 'Provider should have at least one schedule')
        self.assertIn('%s:00<br>\n\t\t\t\t\t\t-<br>\n\t\t\t\t\t\t%s:00' % (start_time, end_time), str(response))
        
        # check if square for day is green
        row_span_string = str(end_time - start_time)
        monday_morning_td = response.html.find('td', attrs={'rowspan': row_span_string})
        self.assertIsNotNone(monday_morning_td, 'schedule td with rowspan %s does not exist' % row_span_string)

        monday_morning_a = monday_morning_td.find('a')
        self.assertIsNotNone(monday_morning_a, 'schedule button does not exist')
        
        # Check the tooltip is now available
        #self.assertEqual(monday_morning_a['title'], 'Disponible', 'Monday morning should be disponible')

        # check if the icon changed
        #monday_morning_i = response.html.find('i', attrs={'id': monday_morning_id})
        #self.assertEqual(monday_morning_i['class'], 'icon-ok-circle', 'Monday morning should be ok icon')


   


    ###
    ### Patient Methods
    ###
    def check_activation_email_patient(self):
        '''             
            1) receive confirmation email
            2) clicks profile activation link
            3) sets a password
        '''
        # check email
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]

        patient = Patient.query(Patient.email == self._TEST_PATIENT_EMAIL).get()
        booking = Booking.query(Booking.patient == patient.key).get()
        
        self.assertEqual(m.subject, 'Rendez-vous Veosan - %s' % 'Ostéopathe')
        
        # assert that activation link is in the email body
        user = User.query(User.key == patient.user).get()
        self.assertTrue('http://localhost/user/activation/%s' % user.signup_token in m.body.payload)
 
        # click link in email
        activation_response = self.testapp.get('/user/activation/%s' % str(user.signup_token))
        
        # choose a password
        activation_response.mustcontain('Votre rendez-vous est confirmé')
        activation_response.mustcontain("Fantastic Fox")
        booking = Booking.query(Booking.patient == patient.key).get()
        activation_response_form = activation_response.forms[0]
        activation_response_form['password'] = self._TEST_PATIENT_PASSWORD
        activation_response_form['password_confirm'] = self._TEST_PATIENT_PASSWORD
        booking_confirm_page = activation_response_form.submit()
        
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('You new appointment is confirmed!')
    
        
    
    def create_test_patient(self):
        '''
            Create a test patient (and linked user) in the datastore
        '''
        user_created, new_user = User.create_user(self._TEST_PATIENT_EMAIL, password_raw=self._TEST_PATIENT_PASSWORD, roles=[auth.PATIENT_ROLE])
        self.assertTrue(user_created)
        tp = Patient()
        tp.created_on = datetime.now()
        tp.user = new_user.key
        tp.first_name = 'Pat'
        tp.last_name = 'Patient'
        tp.email = "pat@patient.com"
        tp.telephone = '514-123-1234'
        tp.terms_agreement = True
        tp.put() 
        
        new_user.language = 'fr'
        new_user.put()
        
   
    def create_provider_and_enable_booking(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        # check profile
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        # enable the booking
        self.login_as_admin()
        enable = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        self.logout_admin()

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Réservez Maintenant")
        
        
    def book_from_public_profile(self, date_string, time_string, patient_email=_TEST_PATIENT_EMAIL, patient_telephone=_TEST_PATIENT_TELEPHONE):
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        schedule_page = public_profile.click(linkid='book_button')
        # Check if a user is logged in
        user_logged_in = 'Déconnexion' in schedule_page
        
        schedule_page.mustcontain("Choisissez la date et l'heure de votre rendez-vous")
        # find the form for next Monday at 10
        form_id = "button-" + date_string + '-' + str(time_string)
        new_patient_page = schedule_page.click(linkid=form_id)
        
        # fill patient info
        step1_form = new_patient_page.forms[0]
        
        if not user_logged_in:
            step1_form['first_name'] = 'Pat'
            step1_form['last_name'] = 'Patient'
            step1_form['telephone'] = patient_telephone        
            step1_form['email'] = patient_email
            step1_form['terms_agreement'] = '1'
        
        step1_form['comments'] = 'I would like to receive care related to boat accident'


        response = step1_form.submit()
            
        if user_logged_in:
            response = response.follow()
            response.mustcontain("Rendez-vous à venir")
                
        else:
            # check email sent page (no user is logged in)
            response.mustcontain("C'est presque complété!")
            response.mustcontain('Un couriel vous a été envoyé')
            response.mustcontain(patient_email)
            response.mustcontain('Contactez-nous')
            
        
    def check_admin_console_for_booking(self, date_string, time_string, patient_email=_TEST_PATIENT_EMAIL, patient_telephone=_TEST_PATIENT_TELEPHONE):
        # check admin console, booking should be in the list
        self.login_as_admin()
        admin_bookings_page = self.testapp.get('/admin/bookings')
        admin_datetime = testutil.next_monday_date_string_alt() + " " + str(time_string) + ":00"
        admin_bookings_page.mustcontain(admin_datetime)
        admin_bookings_page.mustcontain('Fantastic Fox')
        #admin_bookings_page.mustcontain('Pat Patient')
        admin_bookings_page.mustcontain(patient_telephone)
        admin_bookings_page.mustcontain(patient_email)
        admin_bookings_page.mustcontain('Patient not confirmed')
        admin_bookings_page.mustcontain('public profile')
        
        admin_bookings_details = admin_bookings_page.click(linkid="show-1")
        admin_bookings_details.mustcontain('I would like to receive care related to boat accident')
        self.logout_admin()


    def patient_confirms_latest_booking(self, date_string, time_string, set_password=True):

        # check email to patient
        booking_datetime = datetime.strptime(testutil.next_monday_date_string() + " " + str(time_string), '%Y-%m-%d %H')
        french_datetime_string = format_datetime(booking_datetime, "EEEE 'le' d MMMM yyyy", locale='fr_CA') + " à " + format_datetime(booking_datetime, "H:mm", locale='fr_CA')
        
        booking_datetime = datetime.strptime(testutil.next_monday_date_string(), '%Y-%m-%d')
        booking_datetime_string = format_date(booking_datetime, format="d MMM yyyy", locale='fr_CA')
        
        booking_time = datetime.strptime(str(time_string), '%H')
        booking_time_string = format_time(booking_time, format="short", locale='fr')
        
        logging.info('French date time of booking: %s' % french_datetime_string) 
        # check that confirmation emails was sent to patient
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        patient_email_count = len(messages)
        # get last email sent
        m = messages[patient_email_count - 1]
        self.assertEqual(self._TEST_PATIENT_EMAIL, m.to)
        
        # activate account
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        
        self.assertEquals(m.subject, 'Rendez-vous Veosan - Ostéopathe')
        user = db.get_user_from_email(self._TEST_PATIENT_EMAIL)
        # check email content
        self.assertTrue('/user/activation/%s' % user.signup_token in m.body.payload)
        self.assertIn('Bonjour', m.body.payload)
        self.assertIn('Merci', m.body.payload)
        self.assertIn(french_datetime_string, m.body.payload)

        # click the link
        confirmation_page = self.testapp.get('/user/activation/%s' % user.signup_token)
        confirmation_page.mustcontain('Votre rendez-vous est confirmé')
        confirmation_page.mustcontain(booking_time_string)
        confirmation_page.mustcontain(booking_datetime_string)
        confirmation_page.mustcontain("Fantastic Fox")
        
        if set_password:
            # set a password
            password_form = confirmation_page.forms[0]
            password_form['password'] = self._TEST_PATIENT_PASSWORD
            password_form['password_confirm'] = self._TEST_PATIENT_PASSWORD
            booking_confirm_page = password_form.submit().follow()
            
            # patient email in navbar
            booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
            booking_confirm_page.mustcontain('Déconnexion')


    def check_appointment_email_to_provider(self, date_string, time_string, provider_email=_TEST_PROVIDER_EMAIL):
        # Check email to provider    
        messages = self.mail_stub.get_sent_messages(to=provider_email)
        provider_mail_count = len(messages)
        
        # get last email sent
        provider_mail = messages[provider_mail_count - 1]
        self.assertEquals(provider_mail.subject, 'Veosan - Nouveau rendez-vous avec Pat Patient')
        self.assertIn('Vous avez un nouveau rendez-vous', provider_mail.body.payload)

        # check status change in all lists (provider, patient and admin dashboards)
        self.login_as_provider()
        provider_bookings = self.testapp.get('/provider/bookings/' + self._TEST_PROVIDER_VANITY_URL)
        provider_bookings.mustcontain('Pat Patient')
        
        # check datetime
        booking_datetime = datetime.strptime(testutil.next_monday_date_string() + " " + str(time_string), '%Y-%m-%d %H')
        french_datetime_string = format_datetime(booking_datetime, "EEEE 'le' d MMMM yyyy", locale='fr_CA') + " à " + format_datetime(booking_datetime, "H:mm", locale='fr_CA')        
        provider_bookings.mustcontain(french_datetime_string)
        self.logout_provider()
    
