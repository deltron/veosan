# -*- coding: utf-8 -*-

import unittest, data.db as db
from base import BaseTest

class AdminTest(BaseTest):
   
    _PROVIDER_TEST_EMAIL = "unit_test@provider.com"
   
    def test_fill_new_provider_address_correctly(self):
        ''' fill out the new provider's address '''
        
        # init a provider
        self._test_admin_provider_init()
        self._test_fill_new_provider_address_correctly_action()
        
    def test_fill_new_provider_profile_correctly(self):
        ''' fill out the new provider's profile '''
        
        # init a provider
        self._test_admin_provider_init()
        self._test_fill_new_provider_profile_correctly_action()

    def test_fill_new_provider_address_then_modify(self):
        ''' fill out the new provider's address then modify it '''
        
        # init a provider
        self._test_admin_provider_init()
        self._test_fill_new_provider_address_correctly_action()
        self._test_modify_provider_address_action()

        
    def test_provider_schedule_set_one_timeslot(self):
        ''' Enable bookings in one timeslot '''
        
        # init a provider
        self._test_admin_provider_init()
        self._test_provider_schedule_set_one_timeslot_action()
        
        
    def test_complete_profile_creation(self):
        ''' Test init provider with address, profile and one timeslot together '''
        
        # init a provider
        self._test_admin_provider_init()
        # solicit
        self._test_new_provider_solicit()
        # terms agreement
        
        # choose password
        
        # fill all sections
        self._test_fill_new_provider_address_correctly_action()
        self._test_fill_new_provider_profile_correctly_action()
        self._test_provider_schedule_set_one_timeslot_action()
        
        
    def test_admin_provider_init_with_empty_email(self):
        ''' initialize a new provider with no email address (should not be possible) '''
        
        request_variables = { 'provider_email' : '' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        
        # this should fail with an error message
        response.showbrowser()
        
        # check for error message
        response.mustcontain("Addresse courriel invalide.")
        
        # if anything below here is in the response, it's not good!
    
        # Check signs of success
        if "Initialized new provider for " in response:
            self.assertTrue(False, "A provider was created without an email address")


    def test_admin_provider_init_with_invalid_email(self):
        ''' initialize a new provider with invalid address (should not be possible) '''
        
        request_variables = { 'provider_email' : 'aaabbbccc' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        
        # this should fail with an error message
        
        # check for error message
        response.mustcontain("Addresse courriel invalide.")
        
        # if anything below here is in the response, it's not good!
    
        # Check signs of success
        if "Initialized new provider for " in response:
            self.assertTrue(False, "A provider was created without an email address")


    ######################################################################
    ## BELOW HERE ARE LOCAL / REUSABLE UTILITY METHODS TO SET UP A PROFILE
    ######################################################################
     
     
    def _test_admin_provider_init(self):
        ''' initialize a new provider '''
        
        request_variables = { 'provider_email' : 'unit_test@provider.com' }
        response = self.testapp.post('/admin/provider/init', request_variables)

        self.assertEqual(response.status_int, 200)        
        response.mustcontain("Initialized new provider for unit_test@provider.com")
        response.mustcontain("None, None [unit_test@provider.com]")
        
        # check badges are present
        response.mustcontain('<span class="label label-success">new</span>')
        response.mustcontain('<span class="label label-important">missing terms</span>')

        # login

    def _test_new_provider_solicit(self):
        ''' Send email to provider and activate'''
        # get the provider key
        self.login_as_admin()
        provider = db.getProviderFromEmail("unit_test@provider.com")
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/administration', request_variables)
        response.showbrowser()
        response.mustcontain('Provider Administration')
        solicit_form = response.form[0]
        solicit_form.submit()
        # the above should send an email
        messages = self.mail_stub.get_sent_messages(to=_PROVIDER_TEST_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        print str(m)
        
        
    def _test_fill_new_provider_address_correctly_action(self):
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/address', request_variables)
        
        #response.showbrowser()
        address_form = response.forms[0] # address form
        
        # fill out the form
        address_form['title'] = u"Mr."
        address_form['first_name'] = u"Fantastic"
        address_form['last_name'] = u"Fox"
        address_form['credentials'] = u"Ph.D"
        address_form['phone'] = u"555-123-5678"
        address_form['location'] = u"mtl-downtown"
        address_form['address'] = u"123 Main St."
        address_form['city'] = u"Westmount"
        address_form['postal_code'] = u"H1B2C3"
        
        # submit it
        response = address_form.submit()
        
        response.mustcontain("Vos modifications ont été enregistrées.")

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


    def _test_modify_provider_address_action(self):
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/address', request_variables)
        
        address_form = response.forms[0] # address form
        
        # verify form contains correct info
        self.assertEqual(address_form['title'].value, u"Mr.")
        self.assertEqual(address_form['first_name'].value, u"Fantastic")
        self.assertEqual(address_form['last_name'].value, u"Fox")
        self.assertEqual(address_form['credentials'].value, u"Ph.D")
        self.assertEqual(address_form['phone'].value, u"555-123-5678")
        self.assertEqual(address_form['location'].value, u"mtl-downtown")
        self.assertEqual(address_form['address'].value, u"123 Main St.")
        self.assertEqual(address_form['city'].value, u"Westmount")
        self.assertEqual(address_form['postal_code'].value, u"H1B2C3")
        
        # iterate over every field item, find the match in the provider object and check its equality
        # with database
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # make some changes to the form
        address_form['title'] = u"Mrs."
        address_form['first_name'] = u"Linda"
        address_form['last_name'] = u"Otter"
        address_form['credentials'] = u"M.Sc"
        address_form['phone'] = u"555-987-6543"
        address_form['location'] = u"mtl-westisland"
        address_form['address'] = u"321 Primary St."
        address_form['city'] = u"Outremont"
        address_form['postal_code'] = u"C4B5C6"

        # submit it
        response = address_form.submit()
        response.mustcontain("Vos modifications ont été enregistrées.")

        # check values in database
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # iterate over every field item, find the match in the provider object and check its equality
        # possible we miss something here?
        for k in iter(address_form.fields):
            if hasattr(provider, str(k)):
                self.assertEquals(address_form[k].value, getattr(provider, k))

        # go back to the admin page, check the name is updated
        response = self.testapp.get('/admin/providers')
        response.mustcontain("Otter, Linda [unit_test@provider.com]")


        
    def _test_fill_new_provider_profile_correctly_action(self):

        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/profile', request_variables)
         
        profile_form = response.forms[0] # address form
        
        # print profile_form.fields.values()
        
        # fill out the form
        profile_form['category'] = 'osteopath'
        
        profile_form.set('specialty', True, 0) # Sports
        profile_form.set('specialty', True, 2) # Cardio

        profile_form.set('associations', True, 0) # Ordre professionnel de la physiothérapie du Québec (OPPQ)
        profile_form.set('associations', True, 2) # Canadian Academy of Manipulative Physiotherapy (CAMPT)

        profile_form.set('certifications', True, 1) # Active Release Therapy (ART)

        profile_form.set('onsite', True, 0) # onsite visits


        profile_form['start_year'] = '2002'
        profile_form['bio'] = "Areas of interest include treatment and management of spinal conditions with an emphasis on manual therapy and rehabilitative exercise."        
        profile_form['quote'] = "The quick brown fox jumped over the lazy dog."

        # submit it
        response = profile_form.submit()
        response.mustcontain("Vos modifications ont été enregistrées.")

        response.mustcontain("2002")
        response.mustcontain("Areas of interest include treatment and management")
        response.mustcontain("The quick brown fox jumped over the lazy dog")

        # TODO - switch to Beautiful Soup to parse HTML?
        response.mustcontain('input checked id="specialty-0" name="specialty" type="checkbox" value="sports"')        
        response.mustcontain('input checked id="specialty-2" name="specialty" type="checkbox" value="cardiology"')  

        response.mustcontain('input checked id="associations-0" name="associations" type="checkbox" value="oppq"')        
        response.mustcontain('input checked id="associations-2" name="associations" type="checkbox" value="campt"')
        
        response.mustcontain('input checked id="certifications-1" name="certifications" type="checkbox" value="art"')        

        response.mustcontain('input checked class="checkbox" id="onsite" name="onsite" type="checkbox" value="True"')        

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
        
        self.assertIn('oppq', provider.associations)
        self.assertIn('campt', provider.associations)
        self.assertNotIn('cpa', provider.associations)

        self.assertIn('art', provider.certifications)
        self.assertNotIn('mckenzie', provider.certifications)

        self.assertTrue(provider.onsite)

        
    def _test_provider_schedule_set_one_timeslot_action(self):

        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the schedule page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/schedule', request_variables)
        
        # TODO make this more comprehensible ie. monday-8-to-13
        monday_morning_id = '0-8-13'
         
        
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
        request_variables = {'provider_key': provider.key.urlsafe(), 'day_time': monday_morning_id, 'operation': 'add'}
        response = self.testapp.post('/provider/schedule', request_variables)
        
        # no javascript interpretation for jquery so request the page again...
        
        # reload page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/schedule', request_variables)        
        
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
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


    def test_upload_image_to_correct_address(self):
        ''' Upload a test image for the new provider '''
        
        self.test_fill_new_provider_address_correctly()
        
        # get the provider key
        provider = db.getProviderFromEmail("unit_test@provider.com")
        
        # request the address page
        request_variables = { 'key' : provider.key.urlsafe() }
        response = self.testapp.get('/provider/address', request_variables)
        
        photo_form = response.forms[1] # photo form
        
        photo_form['profilePhoto'] = ('profilePhoto', 'provider-test-image.png')
        
        # photo_form.submit()
        
        # hmm can't upload
        # not possible to test blobstore yet...
        
   

if __name__ == "__main__":
    unittest.main()
    
    
