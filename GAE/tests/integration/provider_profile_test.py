# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db
from data.model import User
import util

class ProviderTest(BaseTest):
    
    def test_add_education_to_profile(self):
        self.login_as_admin()
        self.init_new_provider()

        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/admin/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)

        education_form = response.forms['education_form']
        
        education_form['start_year'] = 1998
        education_form['end_year'] = 2002
        education_form['school_name'] = 'mcgill'
        education_form['degree_type'] = 'bachelor'
        education_form['degree_title'] = 'Clinical Physiotherapy'
        education_form['description'] = 'Graduated with honors'

        response = education_form.submit()
        
        # check on the profile admin page
        response.mustcontain('1998-2002')
        response.mustcontain('Université McGill')
        response.mustcontain('Graduated with honors')
        response.mustcontain('Clinical Physiotherapy')
        response.mustcontain("Baccalauréat")
        
        
        # check on the public profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain('1998-2002')
        response.mustcontain('Université McGill')
        response.mustcontain('Graduated with honors')
        response.mustcontain('Clinical Physiotherapy')
        response.mustcontain("Baccalauréat")



    def test_delete_education_from_profile(self):
        self.login_as_admin()
        self.init_new_provider()

        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/admin/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)

        education_form = response.forms['education_form']
        
        education_form['start_year'] = 1998
        education_form['end_year'] = 2002
        education_form['school_name'] = 'mcgill'
        education_form['degree_type'] = 'bachelor'
        education_form['degree_title'] = 'Clinical Physiotherapy'
        education_form['description'] = 'Graduated with honors'

        response = education_form.submit()
        
        response.mustcontain('1998-2002')
        response.mustcontain('Université McGill')
        response.mustcontain('Graduated with honors')
        response.mustcontain('Clinical Physiotherapy')
        response.mustcontain("Baccalauréat")
        
        provider = db.get_provider_from_vanity_url(self._TEST_PROVIDER_VANITY_URL)
        education = provider.get_education().get()

        response_after_delete = self.testapp.get('/admin/provider/profile/cv/education/' + self._TEST_PROVIDER_VANITY_URL + "/delete/" + education.key.urlsafe())


        # education should be gone
        response_after_delete.mustcontain(no='1998-2002')
        response_after_delete.mustcontain(no='Graduated with honors')
        response_after_delete.mustcontain(no='Clinical Physiotherapy')
        # Mcgill and baccalaureat will be in the page because of form drop downs...
        
        # check on the public profile
        public_response_after_delete = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_response_after_delete.mustcontain(no='1998-2002')
        public_response_after_delete.mustcontain(no='Graduated with honors')
        public_response_after_delete.mustcontain(no='Clinical Physiotherapy')
        public_response_after_delete.mustcontain(no='Université McGill')
        public_response_after_delete.mustcontain(no="Baccalauréat")



if __name__ == "__main__":
    unittest.main()
    
    
