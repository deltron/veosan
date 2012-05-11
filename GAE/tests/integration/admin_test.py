# -*- coding: utf-8 -*-

import unittest, webtest
from google.appengine.ext import testbed
import main, db

class AdminTest(unittest.TestCase):
    ''' *** NOTE ***
    
    Settings in app.yaml are ignored by tests
    App assumes login is "magically" handled properly
    
    '''

    def setUp(self):
        # Wrap the app with WebTest’s TestApp.
        self.testapp = webtest.TestApp(main.application)
        
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_blobstore_stub()
        
    def tearDown(self):
        self.testbed.deactivate()

    def test_admin_provider_init(self):
        ''' initialize a new provider '''
        
        request_variables = { 'providerEmail' : 'unit_test@provider.com' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        response.mustcontain("Initialized new provider for unit_test@provider.com")
        response.mustcontain("None, None [unit_test@provider.com]")
        #response.showbrowser()
        

    def test_fill_new_provider_address_correctly(self):
        ''' fill out the new provider's address '''
        
        # init a provider
        self.test_admin_provider_init()
        
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key() }
        response = self.testapp.get('/provider/address', request_variables)
        
        address_form = response.forms[0] # address form
        
        # check email address is pre-populated
        self.assertEqual(address_form['email'].value, "unit_test@provider.com")

        # fill out the form
        address_form['prefix'] = u"Mr."
        address_form['firstName'] = u"Fantastic"
        address_form['lastName'] = u"Fox"
        address_form['postfix'] = u"Ph.D"
        address_form['phone'] = u"555-123-5678"
        address_form['region'] = u"mtl-downtown"
        address_form['address'] = u"123 Main St."
        address_form['city'] = u"Westmount"
        address_form['postalCode'] = u"H1B2C3"
        
        # submit it
        response = address_form.submit()
        response.mustcontain("Saved!")

        # check values in database
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # iterate over every field item, find the match in the provider object and check its equality
        # possible we miss something here?
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # go back to the admin page, check the name is updated
        response = self.testapp.get('/admin/providers')
        response.mustcontain("Fox, Fantastic [unit_test@provider.com]")


    def test_fill_new_provider_profile_correctly(self):
        ''' fill out the new provider's profile '''
        
        # init a provider
        self.test_admin_provider_init()
        
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key() }
        response = self.testapp.get('/provider/profile', request_variables)
         
        profile_form = response.forms[0] # address form
        
       # print profile_form.fields.values()
        
        # fill out the form
        profile_form['category'] = 'osteopath'
        
        profile_form.set('specialty', True, 0) # Sports
        profile_form.set('specialty', True, 2) # Cardio

        profile_form['startYear'] = '2002'
        profile_form['bio'] = "Areas of interest include treatment and management of spinal conditions with an emphasis on manual therapy and rehabilitative exercise."
        
        # submit it
        response = profile_form.submit()
        response.mustcontain("Saved!")

        response.mustcontain("2002")
        response.mustcontain("Areas of interest include treatment and management")

        response.mustcontain('input checked id="specialty-0" name="specialty" type="checkbox" value="sports"')        
        response.mustcontain('input checked id="specialty-2" name="specialty" type="checkbox" value="cardiology"')        
        response.mustcontain('option selected value="osteopath"')
        
        # check values in database
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
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


    def test_upload_image_to_correct_address(self):
        ''' Upload a test image for the new provider '''
        
        self.test_fill_new_provider_address_correctly()
        
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key() }
        response = self.testapp.get('/provider/address', request_variables)
        
        photo_form = response.forms[1] # photo form
        
        photo_form['profilePhoto'] = ('profilePhoto', 'provider-test-image.png')
        
        # photo_form.submit()
        
        # hmm can't upload
        # not possible to test blobstore yet...
        
        
    def test_provider_schedule_set(self):
        ''' fill out the new provider's profile '''
        # init a provider
        self.test_admin_provider_init()
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        # request the schedule page
        request_variables = { 'key' : provider.key() }
        response = self.testapp.get('/provider/schedule', request_variables)
        monday_morning_id = '0-8-13'
        html = response.html
        # Check a ids
        monday_morning_a = html.find('a', attrs={'id': monday_morning_id})
        self.assertTrue(monday_morning_a != None, 'The tag a with id %s should exist'.format(monday_morning_id))
        response.mustcontain(monday_morning_id)
        # Click to select Monday morning
        #jquery_response = response.click(linkid=monday_morning_id, verbose=True)
        
        post_data = {'provider_key': provider.key(), 'day_time': monday_morning_id, 'op': 'add'}
        jquery_response = self.testapp.post('/provider/schedule', post_data)
        # TODO check the jQuery response
        # reload page
        response = self.testapp.get('/provider/schedule', request_variables)
        
        provider = db.getProviderFromEmail("unit_test@provider.com")
        schedule_count = provider.schedule.count()
        print ('Provider has %s schedules' % schedule_count)

        self.assertEqual(schedule_count , 1, 'Provider should have a schedule')
        monday_morning_a = html.find('a', attrs={'id': monday_morning_id})
        print 'Class:' + monday_morning_a['class']
        self.assertEqual(monday_morning_a['class'], 'btn btn-mini btn-success', 'Monday morning should be green')
        

if __name__ == "__main__":
    unittest.main()
    
    
