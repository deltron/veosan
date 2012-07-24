# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderTest(BaseTest):
    
    def test_add_education_to_profile(self):
        self.login_as_admin()
        self.init_new_provider()

        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        education_form = response.forms['education_form']
        
        education_form['start_year'] = 1998
        education_form['end_year'] = 2002
        education_form['school_name'] = 'mcgill'
        education_form['degree_type'] = 'bachelor'
        education_form['degree_title'] = 'Clinical Physiotherapy'
        education_form['description'] = 'Graduated with honors'

        response = education_form.submit()
        
        # check on the profile admin page
        response.mustcontain('1998','2002')
        response.mustcontain('Université McGill')
        response.mustcontain('Graduated with honors')
        response.mustcontain('Clinical Physiotherapy')
        response.mustcontain("Baccalauréat")
        
        
        # check on the public profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain('1998','2002')
        response.mustcontain('Université McGill')
        response.mustcontain('Graduated with honors')
        response.mustcontain('Clinical Physiotherapy')
        response.mustcontain("Baccalauréat")

        # check the event log
        self.assert_msg_in_log("Edit CV: add education success", admin=True)



    def test_delete_education_from_profile(self):
        self.login_as_admin()
        self.init_new_provider()

        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        education_form = response.forms['education_form']
        
        education_form['start_year'] = 1998
        education_form['end_year'] = 2002
        education_form['school_name'] = 'mcgill'
        education_form['degree_type'] = 'bachelor'
        education_form['degree_title'] = 'Clinical Physiotherapy'
        education_form['description'] = 'Graduated with honors'

        response = education_form.submit()
        
        response.mustcontain('1998','2002')
        response.mustcontain('Université McGill')
        response.mustcontain('Graduated with honors')
        response.mustcontain('Clinical Physiotherapy')
        response.mustcontain("Baccalauréat")
        
        provider = db.get_provider_from_vanity_url(self._TEST_PROVIDER_VANITY_URL)
        education = provider.get_education()[0]

        response_after_delete = self.testapp.get('/provider/cv/education/' + self._TEST_PROVIDER_VANITY_URL + "/delete/" + education.key.urlsafe())


        # education should be gone
        response_after_delete.mustcontain(no='1998')
        response_after_delete.mustcontain(no='2002')
        response_after_delete.mustcontain(no='Graduated with honors')
        response_after_delete.mustcontain(no='Clinical Physiotherapy')
        # Mcgill and baccalaureat will be in the page because of form drop downs...
        
        # check on the public profile
        public_response_after_delete = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_response_after_delete.mustcontain(no='1998')
        public_response_after_delete.mustcontain(no='2002')
        public_response_after_delete.mustcontain(no='Graduated with honors')
        public_response_after_delete.mustcontain(no='Clinical Physiotherapy')
        public_response_after_delete.mustcontain(no='Université McGill')
        public_response_after_delete.mustcontain(no="Baccalauréat")

        self.assert_msg_in_log("Edit CV: delete education success", admin=True)


    def test_add_experience_to_profile(self):
        self.login_as_admin()
        self.init_new_provider()

        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['experience_form']
        
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = 'Manual Physiotherapy'
        experience_form['description'] = 'Worked with my hands'

        response = experience_form.submit()
        
        # check on the profile admin page
        response.mustcontain('2003','2006')
        response.mustcontain('Kinatex')
        response.mustcontain('Manual Physiotherapy')
        response.mustcontain('Worked with my hands')
        
        
        # check on the public profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain('2003','2006')
        response.mustcontain('Kinatex')
        response.mustcontain('Manual Physiotherapy')
        response.mustcontain('Worked with my hands')

        self.assert_msg_in_log("Edit CV: add experience success", admin=True)


    def test_delete_experience_from_profile(self):
        self.login_as_admin()
        self.init_new_provider()

        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['experience_form']
        
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = 'Manual Physiotherapy'
        experience_form['description'] = 'Worked with my hands'

        response = experience_form.submit()
        
        # check on the profile admin page
        response.mustcontain('2003','2006')
        response.mustcontain('Kinatex')
        response.mustcontain('Manual Physiotherapy')
        response.mustcontain('Worked with my hands')
        
        
        # check on the public profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain('2003','2006')
        response.mustcontain('Kinatex')
        response.mustcontain('Manual Physiotherapy')
        response.mustcontain('Worked with my hands')


        
        provider = db.get_provider_from_vanity_url(self._TEST_PROVIDER_VANITY_URL)
        education = provider.get_experience()[0]

        response_after_delete = self.testapp.get('/provider/cv/experience/' + self._TEST_PROVIDER_VANITY_URL + "/delete/" + education.key.urlsafe())


        # experience should be gone
        response_after_delete.mustcontain(no='2003')
        response_after_delete.mustcontain(no='2006')
        response_after_delete.mustcontain(no='Kinatex')
        response_after_delete.mustcontain(no='Manual Physiotherapy')
        response_after_delete.mustcontain(no='Worked with my hands')
                
        # check on the public profile
        public_response_after_delete = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_response_after_delete.mustcontain(no='2003')
        public_response_after_delete.mustcontain(no='2006')
        public_response_after_delete.mustcontain(no='Kinatex')
        public_response_after_delete.mustcontain(no='Manual Physiotherapy')
        public_response_after_delete.mustcontain(no='Worked with my hands')

        self.assert_msg_in_log("Edit CV: delete experience success", admin=True)

    def test_uncheck_specialties(self):
        self.login_as_admin()
        self.init_new_provider()
        
        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)

        profile_form = response.forms[0] # address form
        profile_form.set('specialty', False, 0) # Sports
        profile_form.set('specialty', False, 2) # Cardio

        response = profile_form.submit()
        
        # verify unchecked
        response.mustcontain('input id="specialty-0" name="specialty" type="checkbox" value="sports"')        
        response.mustcontain('input id="specialty-2" name="specialty" type="checkbox" value="cardiology"')  

        # navigate away
        self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        # navigate back
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain('input id="specialty-0" name="specialty" type="checkbox" value="sports"')        
        response.mustcontain('input id="specialty-2" name="specialty" type="checkbox" value="cardiology"')  
        response.mustcontain(no='input checked id="specialty-0" name="specialty" type="checkbox" value="sports"')        
        response.mustcontain(no='input checked id="specialty-2" name="specialty" type="checkbox" value="cardiology"')  
        
        self.assert_msg_in_log("Edit Profile: Success", admin=True)


if __name__ == "__main__":
    unittest.main()
    
    
