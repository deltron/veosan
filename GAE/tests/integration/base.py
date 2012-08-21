# -*- coding: utf-8 -*-

from google.appengine.ext import testbed
import os, logging
import unittest, webtest
from StringIO import StringIO



# veo
import main
import data.db as db
from handler import auth
from data.model import Patient
from datetime import datetime
from data.model import User, Booking
import util, testutil
from google.appengine.datastore import datastore_stub_util

class BaseTest(unittest.TestCase):
    util.BOOKING_ENABLED = True
    
    ''' *** NOTE ***
    
    Settings in app.yaml are ignored by tests
    App assumes login is "magically" handled properly
    
    '''    
       
    _TEST_PROVIDER_EMAIL = "unit_test@provider.com"
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


    def assert_msg_in_log(self, msg, admin = False):
        events = db.get_events_all()
        log_present = False
        try:
            # usual case is there is > 1 result
            log_present = any((msg in event.description and event.admin == admin) for event in events)
        except TypeError:
            # if there is only one, check it
            log_present = msg in events.description and events.admin == admin
        
        self.assertTrue(log_present, "Event log message missing: %s, admin=%s" % (msg,admin))


    
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
        

    def logout_provider(self):
        logout_redirect = self.testapp.get('/logout')
        logout_response = logout_redirect.follow()
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
        login_welcome_page.mustcontain('Upcoming Appointments')
        
        
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
        response = self.testapp.get('/lang/fr')
        
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = first_name
        signup_form['last_name'] = last_name
        signup_form['email'] = email
        signup_form['postal_code'] = 'h1h1h1'
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
        address_form = response.forms['address_form'] # address form
        
        # fill out the form
        address_form['title'] = u"mr"
        address_form['first_name'] = u"Fantastic"
        address_form['last_name'] = u"Fox"
        address_form['phone'] = u"555-123-5678"
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
        self.assertEqual(address_form['phone'].value, u"555-123-5678")
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
        
        # print profile_form.fields.values()
        
        # fill out the form        
        profile_form.set('specialty', True, 0) # Sports
        profile_form.set('specialty', True, 2) # Cardio

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
        response.mustcontain('input checked id="specialty-0" name="specialty" type="checkbox" value="sports"')        
        response.mustcontain('input checked id="specialty-2" name="specialty" type="checkbox" value="cardiology"')  

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
        
        
        self.assertIn('sports', provider.specialty)
        self.assertIn('cardiology', provider.specialty)
        self.assertNotIn('geriatric', provider.specialty)
        
        self.assertIn('onsite', provider.practice_sites)

        # check the event log
        #self.assert_msg_in_log("Edit Profile: Success", admin=as_admin)


    def provider_schedule_set_one_timeslot_action(self):

        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # request the schedule page
        response = self.testapp.get('/provider/schedule/%s' % provider.vanity_url)
        
        # Check that schedule is empty

        # Add an available schedule Monday morning 9-12   
        response = self.testapp.get('/provider/schedule/%s/add/monday/9' % provider.vanity_url)
    
        schedule_form = response.forms['schedule_form']
        
        # check the form selects are filled with values
        
        schedule_form['day'] = 'monday'
        schedule_form['start_time'] = 9
        schedule_form['end_time'] = 12
        response = schedule_form.submit()
        
        provider = db.get_provider_from_email("unit_test@provider.com")
        
        # check one schedule was saved in the database
        schedule_count = provider.get_schedules().count()
        self.assertEqual(schedule_count , 1, 'Provider should have a schedule')
        response.mustcontain('9h-12h')
        
        # check if square for day is green
        monday_morning_td = response.html.find('td', attrs={'rowspan': '3'})
        logging.info('TSET: %s ' % monday_morning_td.__class__)
        self.assertIsNotNone(monday_morning_td, 'schedule td with rowspan 3 does not exist')

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

    def book_appointment(self, category, date_string, hour_string):
        '''
            Go to index, fill the form and return the response
        '''
        result_response = self.testapp.post('/')
        booking_form = result_response.forms[0] # booking form  
        # check that date requested is in date select list
        booking_date_select = booking_form.fields['booking_date'][0]
        self.assertIn(date_string, [x[0] for x in booking_date_select.options]) 
        # fill out the form
        booking_form['category'] = category
        booking_form['booking_date'] = date_string
        booking_form['booking_time'] = hour_string

        result_response = booking_form.submit()
        
        return result_response
    
    def fill_booking_email_form(self, result_response, email=None):
        # email form (second form on page)        
        hidden_form = result_response.forms[0]
        email_form = result_response.forms[1]
        # Replacing: new_patient_response = email_form.submit()
        # Hack to post directly and make tests run.
        # Warning: We are not testing the form and javascript on this page
        post_data = {
                     'bk': email_form['bk'].value,
                     'provider_key': hidden_form['provider_key'].value,
                     'booking_datetime': hidden_form['booking_datetime'].value,
                     'index': hidden_form['index'].value
                    }
        if email:
            post_data['email'] = email
        action = str(email_form.action)
        new_patient_response = self.testapp.post(action, params=post_data)        
        return new_patient_response
        
    
    def fill_new_patient_profile(self, response):
        response.mustcontain('Nouveau patient')
        patient_form = response.forms[0]
        patient_form['first_name'] = 'Pat'
        patient_form['last_name'] = 'Patient'
        patient_form['telephone'] = '514-123-1234'
        patient_form['terms_agreement'] = '1'
        patient_form['address'] = '123 High Street'
        patient_form['city'] = 'Montreal'
        patient_form['postal_code'] = 'H2H 2Y2'
        booking_confirm_response = patient_form.submit()
        # check confirm page
        booking_confirm_response.mustcontain("C'est presque complété!")
        booking_confirm_response.mustcontain(self._TEST_PATIENT_EMAIL)
        return booking_confirm_response
    
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
        activation_response.mustcontain("Fantastic F.")
        booking = Booking.query(Booking.patient == patient.key).get()
        activation_response_form = activation_response.forms[0]
        activation_response_form['password'] = self._TEST_PATIENT_PASSWORD
        activation_response_form['password_confirm'] = self._TEST_PATIENT_PASSWORD
        booking_confirm_page = activation_response_form.submit()
        
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you %s!' % patient.first_name)
    
        
    
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
        
        
    def book_from_public_profile(self, date_string, time_string):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        # check profile
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        # enable the booking
        self.login_as_admin()
        enable = self.testapp.post('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Réservez Maintenant")
        self.logout_admin()
        
        schedule_page = public_profile.click(linkid='book_button')
        schedule_page.mustcontain("Choisissez la date et l'heure de votre rendez-vous")
        # find the form for next Monday at 10
        form_id = "button-" + date_string + '-' + time_string
        new_patient_page = schedule_page.click(linkid=form_id)
        
        # fill patient info
        step1_form = new_patient_page.forms[0]
        step1_form['email'] = self._TEST_PATIENT_EMAIL
        step1_form['telephone'] = self._TEST_PATIENT_TELEPHONE
        step1_form['comments'] = 'I would like to receive sports related care'
        step1_form['specialty'] = 'sports'
        step1_form['insurance'] = 'private'

        new_patient_page = step1_form.submit()
        email_sent_page = self.fill_new_patient_profile(new_patient_page)
        # check email sent page
        email_sent_page.mustcontain('Merci Pat')
        email_sent_page.mustcontain('Un couriel vous a été envoyé')
        email_sent_page.mustcontain(self._TEST_PATIENT_EMAIL)
        email_sent_page.mustcontain('Contactez-nous')
        
        # check admin console, booking should be in the list
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
        
        admin_bookings_details = admin_bookings_page.click(linkid="show-1")
        admin_bookings_details.mustcontain('Assurance privée')
        admin_bookings_details.mustcontain('I would like to receive sports related care')
        admin_bookings_details.mustcontain('sports')
                                           
        self.logout_admin()
