# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderTest(BaseTest):
    def test_step_through_profile_completion(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        # step 1 - bio and quote
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("<li>Write your bio and quote</li>")
        
        profile_form = response.forms['profile_form']
        profile_form['bio'] = 'This is my biography more words long!'
        response = profile_form.submit()
        response.mustcontain("<li>Write your bio and quote</li>")

        profile_form = response.forms['profile_form']
        profile_form['quote'] = 'This is my quote hello goodbye!'
        response = profile_form.submit().follow()
        # redirects you to CV page for next step
        response.mustcontain("Curriculum Vitae")

        # check if it's struck out
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("<li><del>Write your bio and quote</del>")

        # fill out the CV
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)
        experience_form = response.forms['experience_form']
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = 'Manual Physiotherapy'
        experience_form['description'] = 'Par1\n\nPar2* Worked with my hands\n * Item two'
        experience_form.submit()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)
        experience_form = response.forms['education_form']
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['school_name'] = 'mcgill'
        experience_form.submit()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)
        experience_form = response.forms['organization_form']
        experience_form['start_year'] = 1992
        experience_form['organization'] = 'odq'
        experience_form.submit()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)
        experience_form = response.forms['continuing_education_form']
        experience_form['title'] = 'SomeEd'
        experience_form['year'] = '2008'
        experience_form.submit()

        # check if it's struck out
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("<li><del>Fill in your CV</del>")

        # fill the address
        response = self.testapp.get('/provider/address/%s' % self._TEST_PROVIDER_VANITY_URL)
        
        address_form = response.forms[0] # address form
        
        # fill out the form
        address_form['title'] = u"mr"
        address_form['first_name'] = u"Fantastic"
        address_form['last_name'] = u"Fox"
        address_form['phone'] = u"555-123-5678"
        address_form['address'] = u"123 Main St."
        address_form['city'] = u"Westmount"
        address_form['postal_code'] = u"H1B2C3"
        address_form.submit()

        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("<li><del>Complete your address</del>")


    def test_change_save_button_less_than_3_cv_items(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        
        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Prochaine étape: ajouter quelque chose à votre CV")

        # add one thing to the CV (1)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['experience_form']
        
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = 'Manual Physiotherapy'
        experience_form['description'] = 'Par1\n\nPar2* Worked with my hands\n * Item two'

        response = experience_form.submit()
        
        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Prochaine étape: ajouter quelque chose à votre CV")

        # add another thing to the CV (2)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['education_form']
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['school_name'] = 'mcgill'
        experience_form.submit()

        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Prochaine étape: ajouter quelque chose à votre CV")

        # add another thing to the CV (3)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['organization_form']
        experience_form['start_year'] = 1992
        experience_form['organization'] = 'odq'
        experience_form.submit()

        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Prochaine étape: ajouter quelque chose à votre CV")

        # add another thing to the CV (4)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['continuing_education_form']
        experience_form['title'] = 'SomeEd'
        experience_form.submit()

        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Prochaine étape: ajouter quelque chose à votre CV")
        
        response2 = response.forms[0].submit().follow()
        response2.mustcontain("Curriculum Vitae")

        # add another thing to the CV (4)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)
        
        experience_form = response.forms['continuing_education_form']
        experience_form['title'] = 'SomeEd'
        experience_form['year'] = '2008'
        experience_form.submit()

        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no="Prochaine étape: ajouter quelque chose à votre CV")


if __name__ == "__main__":
    unittest.main()
    
    
