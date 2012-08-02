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
import util
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
    
    _TEST_PROVIDER_VANITY_URL = 'bobafett'

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
        
        
    def login_as_provider(self):
        ''' login as a provider, assumes already initialized and accepted terms '''
        response = self.testapp.get('/login')
        
        login_form = response.forms[0]
        login_form['email'] = self._TEST_PROVIDER_EMAIL
        login_form['password'] = self._TEST_PROVIDER_PASSWORD
        login_redirect = login_form.submit()
        response = login_redirect.follow()
        
        # default page for provider after login is bookings
        response.mustcontain("Profil")
        
        # check the event log
        self.assert_msg_in_log("Provider Logged In")

        return response
        

    def logout_provider(self):
        logout_redirect = self.testapp.get('/logout')
        logout_response = logout_redirect.follow()
        logout_response.mustcontain('Mon Compte')
        
        # check the event log
        self.assert_msg_in_log("Logged out")

    
    def login_as_patient(self):
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
    
    # this is the old way
    def create_complete_provider_profile(self):
        '''
            Test init provider with address, profile and one timeslot together.
            This happens in two strokes:
            1. The admin create the profile and solicits the provider
            2. The provider receives the email and activates his account
            
            There is one timeslot available (Monday at 8am)
        '''
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
        self.activate_provider_from_email()
        # logout
        self.logout_provider()

     
    def self_signup_provider(self, provider_email=_TEST_PROVIDER_EMAIL, vanity_url=_TEST_PROVIDER_VANITY_URL):
        response = self.testapp.post('/signup/provider')
        
        signup_form = response.forms['provider_signup_form']
        signup_form['first_name'] = 'first'
        signup_form['last_name'] = 'last'
        signup_form['email'] = provider_email
        signup_form['postal_code'] = 'h1h1h1'
        response = signup_form.submit()

        signup_form2 = response.forms['provider_signup_form2']
        signup_form2['category'] = 'osteopath'
        signup_form2['vanity_url'] = vanity_url
        signup_form2['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form2['password_confirm'] = self._TEST_PROVIDER_PASSWORD

        profile_response = signup_form2.submit().follow()
        profile_response.mustcontain("Bienvenue")
        
             
    def init_new_provider(self, provider_email=_TEST_PROVIDER_EMAIL, vanity_url=_TEST_PROVIDER_VANITY_URL):
        ''' initialize a new provider '''
        
        request_variables = { 'provider_email' : provider_email, 'vanity_url' : vanity_url}
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        response.mustcontain("Initialized new provider for %s" % provider_email)
        response.mustcontain("new")
        response.mustcontain("missing terms")
        response.mustcontain(provider_email)
        
        # check badges are present
        response.mustcontain('<span class="label label-success">new</span>')
        response.mustcontain('<span class="label label-important">missing terms</span>')


    def solicit_provider(self):
        ''' Send email to provider and activate'''
        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        response = self.testapp.get('/admin/provider/admin/%s' % provider.vanity_url)

        response.mustcontain('Provider Administration')
        
        # hit the solicit button
        response = self.testapp.get('/admin/provider/solicit/%s' % provider.vanity_url)
        
        response = self.testapp.get("/")
        
        # read the email and check content
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        self.assertEqual(m.subject, 'Activation de votre compte Veosan')
        
        # assert that activation link is in the email body
        user = db.get_user_from_email(self._TEST_PROVIDER_EMAIL)
        self.assertTrue('http://localhost/user/activation/%s' % user.signup_token in m.body.payload)
 

        
    def fill_new_provider_address_correctly_action(self):
        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # request the address page
        response = self.testapp.get('/provider/address/%s' % provider.vanity_url)
        
        address_form = response.forms[0] # address form
        
        # fill out the form
        address_form['title'] = u"mr"
        address_form['first_name'] = u"Fantastic"
        address_form['last_name'] = u"Fox"
        address_form['credentials'] = u"Ph.D"
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
        response = self.testapp.get('/admin/providers')
        response.mustcontain("Fox")
        response.mustcontain("unit_test@provider.com")
        
        # check the event log
        self.assert_msg_in_log("Edit Address: Success", admin=True)

    def modify_provider_address_action(self):
        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # request the address page
        response = self.testapp.get('/provider/address/%s' % provider.vanity_url)
        
        address_form = response.forms[0] # address form
        
        # verify form contains correct info
        self.assertEqual(address_form['title'].value, u"mr")
        self.assertEqual(address_form['first_name'].value, u"Fantastic")
        self.assertEqual(address_form['last_name'].value, u"Fox")
        self.assertEqual(address_form['credentials'].value, u"Ph.D")
        self.assertEqual(address_form['phone'].value, u"555-123-5678")
        self.assertEqual(address_form['address'].value, u"123 Main St.")
        self.assertEqual(address_form['city'].value, u"Westmount")
        self.assertEqual(address_form['postal_code'].value, u"H1B2C3")

        
        # iterate over every field item, find the match in the provider object and check its equality
        # with database
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # make some changes to the form
        address_form['title'] = u"mrs"
        address_form['first_name'] = u"Linda"
        address_form['last_name'] = u"Otter"
        address_form['credentials'] = u"M.Sc"
        address_form['phone'] = u"555-987-6543"
        address_form['address'] = u"321 Primary St."
        address_form['city'] = u"Outremont"
        address_form['postal_code'] = u"C4B5C6"


        # submit it
        response = address_form.submit()
        response.mustcontain("Vos modifications ont été enregistrées.")

        # check values in database
        provider = db.get_provider_from_email("unit_test@provider.com")
        
        # iterate over every field item, find the match in the provider object and check its equality
        # possible we miss something here?
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # go back to the admin page, check the name is updated
        response = self.testapp.get('/admin/providers')
        response.mustcontain("Otter")
        response.mustcontain("Linda")
        response.mustcontain("unit_test@provider.com")

        # check the event log
        self.assert_msg_in_log("Edit Address: Success", admin=True)

        
    def fill_new_provider_profile_correctly_action(self, as_admin=True):

        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # request the address page
        response = self.testapp.get('/provider/profile/%s' % provider.vanity_url)
         
        profile_form = response.forms[0] # address form
        
        # print profile_form.fields.values()
        
        # fill out the form
        profile_form['category'] = 'osteopath'
        
        profile_form.set('specialty', True, 0) # Sports
        profile_form.set('specialty', True, 2) # Cardio

        profile_form.set('practice_sites', True, 0) # onsite visits


        profile_form['bio'] = "Areas of interest include treatment and management of spinal conditions with an emphasis on manual therapy and rehabilitative exercise."        
        profile_form['quote'] = "The quick brown fox jumped over the lazy dog."

        # submit it (redirected to CV because not complete)
        response = profile_form.submit().follow()
        response.mustcontain("Curriculum Vitae")
        
        # go back to the profile page
        
        response = self.testapp.get('/provider/profile/%s' % provider.vanity_url)

        response.mustcontain("Areas of interest include treatment and management")
        response.mustcontain("The quick brown fox jumped over the lazy dog")

        # TODO - switch to Beautiful Soup to parse HTML?
        response.mustcontain('input checked id="specialty-0" name="specialty" type="checkbox" value="sports"')        
        response.mustcontain('input checked id="specialty-2" name="specialty" type="checkbox" value="cardiology"')  

        response.mustcontain('input checked id="practice_sites-0" name="practice_sites" type="checkbox" value="onsite"')        

        response.mustcontain('option selected value="osteopath"')
        
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
        self.assert_msg_in_log("Edit Profile: Success", admin=as_admin)


    def provider_schedule_set_one_timeslot_action(self):

        # get the provider key
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        
        # request the schedule page
        response = self.testapp.get('/provider/schedule/%s' % provider.vanity_url)
        
        # TODO make this more comprehensible ie. monday-8-to-13
        monday_morning_id = '0-8-12'
        
        # Check a ids
        monday_morning_a = response.html.find('a', attrs={'id': monday_morning_id})
        self.assertTrue(monday_morning_a != None, 'The tag a with id %s should exist'.format(monday_morning_id))
        response.mustcontain(monday_morning_id)
        
        # Check the square is grayed out
        self.assertEqual(monday_morning_a['class'], 'btn btn-mini', 'Monday morning should be gray box')

        # Check the tooltip unavailable
        self.assertEqual(monday_morning_a['title'], 'Non-disponible', 'Monday morning should be non disponible')

        # Check the icon is a circle with cross
        monday_morning_i = response.html.find('i', attrs={'id': monday_morning_id})
        self.assertEqual(monday_morning_i['class'], 'icon-ban-circle', 'Monday morning should be ban icon')


        # Click to select Monday morning        
        request_variables = {'day_time': monday_morning_id, 'operation': 'add'}
        response = self.testapp.post(str('/provider/schedule/%s' % provider.vanity_url), request_variables)
        
        # no javascript interpretation for jquery so request the page again...
        
        # reload page
        response = self.testapp.get(str('/provider/schedule/%s' % provider.vanity_url))
        
        provider = db.get_provider_from_email("unit_test@provider.com")
        
        # check one schedule was saved in the database
        schedule_count = provider.get_schedule().count()
        self.assertEqual(schedule_count , 1, 'Provider should have a schedule')
        
        # check if square for day is green
        monday_morning_a = response.html.find('a', attrs={'id': monday_morning_id})
        self.assertEqual(monday_morning_a['class'], 'btn btn-mini btn-success', 'Monday morning should be green')

        # Check the tooltip is now available
        self.assertEqual(monday_morning_a['title'], 'Disponible', 'Monday morning should be disponible')

        # check if the icon changed
        monday_morning_i = response.html.find('i', attrs={'id': monday_morning_id})
        self.assertEqual(monday_morning_i['class'], 'icon-ok-circle', 'Monday morning should be ok icon')


   
    def activate_provider_from_email(self):
        '''
            Click on activation link, 
        '''
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        # terms page
        user = User.query(User.key == provider.user).get()

        activation_url = 'http://localhost/user/activation/%s' % user.signup_token
        terms_response = self.testapp.get(activation_url)
        terms_response.mustcontain("J'accepte les conditions d'utilisation")
        terms_form = terms_response.forms[0]
        terms_form['terms_agreement'] = '1'
        # password page
        password_choice_response = terms_form.submit()
        password_choice_response = password_choice_response.follow()
        
        password_choice_response.mustcontain('Choisissez votre mot de passe')
        password_form = password_choice_response.forms[0]
        password_form['password'] = self._TEST_PROVIDER_PASSWORD
        password_form['password_confirm'] = self._TEST_PROVIDER_PASSWORD

        welcome_response = password_form.submit()
        welcome_response = welcome_response.follow()
        self.assertEqual(welcome_response.status_int, 200)
        welcome_response.mustcontain(u'Bienvenue chez Veosan!')

        self.assert_msg_in_log("New account created for user")

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
        # leave region to default (should be downtown)
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
        booking_confirm_response.mustcontain("An email was sent with your appointment details and a confirmation code.")
        booking_confirm_response.mustcontain("Please check your inbox and click on the link to finish the process.")
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
        
        self.assertEqual(m.subject, 'veosan reservation - %s' % 'Ostéopathe')
        
        # assert that activation link is in the email body
        user = User.query(User.key == patient.user).get()
        self.assertTrue('http://localhost/user/activation/%s' % user.signup_token in m.body.payload)
 
        # click link in email
        activation_response = self.testapp.get('/user/activation/%s' % str(user.signup_token))
     
      
        # choose a password
        activation_response.mustcontain('Choisissez votre mot de passe')
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
        
