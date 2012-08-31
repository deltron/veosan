# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderTest(BaseTest):
    
    def test_add_education_to_profile(self):
        self.self_signup_provider()
        
        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        education_form = response.forms['education_form']
        
        education_form['start_year'] = 1998
        education_form['end_year'] = 2002
        education_form['school_name'] = 'Université McGill'
        education_form['degree_type'] = 'bachelor'
        education_form['degree_title'] = 'Clinical Physiotherapy'
        education_form['description'] = 'Graduated with honors'

        response = education_form.submit().follow()
        
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
        #self.assert_msg_in_log("Edit CV: add education success", admin=True)

    def test_add_organization_nothing_and_other(self):
        self.self_signup_provider()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        education_form = response.forms['organization_form']
        
        education_form['start_year'] = 1998
        education_form['end_year'] = 2002
        education_form['organization'] = 'nothing'

        response = education_form.submit()
                
        # error should appear asking to choose something
        response.mustcontain('1998','2002')
        response.mustcontain("SVP choisir une option. Si aucun choix ne")

        education_form2 = response.forms['organization_form']
        
        education_form2['organization'] = 'other'
        response2 = education_form2.submit()

        # error should appear asking to write in other
        response2.mustcontain("SVP entrez le nom de")

        education_form3 = response2.forms['organization_form']
        education_form3['other'] = 'Curtain University'
        response3 = education_form3.submit().follow()
        
        response3.mustcontain('Curtain University')
        
        # check on the public profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain('1998','2002')
        response.mustcontain('Curtain University')

        # check the event log
        self.assert_msg_in_log("Edit CV: add organization success", admin=False)

    def test_everything_correct_then_edit_and_change_valid_field_to_invalid(self):
        self.self_signup_provider()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        education_form = response.forms['education_form']
        
        education_form['start_year'] = 1998
        education_form['end_year'] = 2002
        education_form['school_name'] = 'Curtain University'
        education_form['degree_type'] = 'bachelor'
        education_form['degree_title'] = 'Clinical Physiotherapy'
        education_form['description'] = 'Graduated with honors'

        response = education_form.submit().follow()
                
        # all good
        response.mustcontain('1998','2002')
        response.mustcontain('Graduated with honors')
        response.mustcontain('Clinical Physiotherapy')
        response.mustcontain("Baccalauréat")
        response.mustcontain("Curtain University")

        # now edit
        provider = db.get_provider_from_vanity_url(self._TEST_PROVIDER_VANITY_URL)
        education = provider.get_education()[0]
        education_key = education.key.urlsafe()
        edit_response = self.testapp.get('/provider/cv/education/' + self._TEST_PROVIDER_VANITY_URL + '/edit/' + education_key)
                
        # change a valid field to invalid       
        edit_form = edit_response.forms['education_form']
        edit_form['start_year'] = 19988991
        error_response = edit_form.submit()
        
        error_response.mustcontain('SVP entrez une année valide.')
        error_response.mustcontain('19988991')

        # now change it to valid again
        edit_form_corrected = error_response.forms['education_form']
        edit_form_corrected['start_year'] = 1979
        saved_response = edit_form_corrected.submit().follow()
        saved_response.mustcontain('1979')

        
        # check the event log
        self.assert_msg_in_log("Edit CV: add education success", admin=False)


    def test_delete_education_from_profile(self):
        self.self_signup_provider()

        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        education_form = response.forms['education_form']
        
        education_form['start_year'] = 1998
        education_form['end_year'] = 2002
        education_form['school_name'] = 'Université McGill'
        education_form['degree_type'] = 'bachelor'
        education_form['degree_title'] = 'Clinical Physiotherapy'
        education_form['description'] = 'Graduated with honors'

        response = education_form.submit().follow()
        
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

        self.assert_msg_in_log("Edit CV: delete education success", admin=False)


    def test_add_experience_to_profile(self):
        self.self_signup_provider()
        
        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['experience_form']
        
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = 'Manual Physiotherapy'
        experience_form['description'] = 'Worked with my hands'

        response = experience_form.submit().follow()
        
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

        #self.assert_msg_in_log("Edit CV: add experience success", admin=True)


    def test_delete_experience_from_profile(self):
        self.self_signup_provider()

        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['experience_form']
        
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = 'Manual Physiotherapy'
        experience_form['description'] = 'Worked with my hands'

        response = experience_form.submit().follow()
        
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

        self.assert_msg_in_log("Edit CV: delete experience success", admin=False)

    def test_add_experience_to_profile_with_markdown(self):
        self.self_signup_provider()


        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['experience_form']
        
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['company_name'] = 'Kinatex'
        experience_form['title'] = 'Manual Physiotherapy'
        experience_form['description'] = 'Par1\n\nPar2* Worked with my hands\n * Item two'

        response = experience_form.submit().follow()
        
        # check on the profile admin page
        response.mustcontain('2003','2006')
        response.mustcontain('Kinatex')
        response.mustcontain('Manual Physiotherapy')
        response.mustcontain('<p>Par1</p>')
        
        
        # check on the public profile
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain('2003','2006')
        response.mustcontain('Kinatex')
        response.mustcontain('Manual Physiotherapy')
        response.mustcontain('Worked with my hands')

        self.assert_msg_in_log("Edit CV: add experience success", admin=False)



    def test_change_save_button_less_than_3_cv_items(self):
        self.self_signup_provider()
        # fill profile section
        self.fill_new_provider_profile_correctly_action()

        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)

        # add one thing to the CV
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
        response.mustcontain("Remplissez votre CV")

        # add another thing to the CV (1)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['education_form']
        experience_form['start_year'] = 2003
        experience_form['end_year'] = 2006
        experience_form['school_name'] = 'mcgill'
        experience_form.submit()

        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Remplissez votre CV")

        # add another thing to the CV (2)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['organization_form']
        experience_form['start_year'] = 1992
        experience_form['organization'] = 'odq'
        experience_form.submit()

        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Remplissez votre CV")

        # add another thing to the CV (3)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)

        experience_form = response.forms['continuing_education_form']
        experience_form['title'] = 'SomeEd'
        experience_form.submit()

        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Remplissez votre CV")

        # add another thing to the CV (4)
        response = self.testapp.get('/provider/cv/' + self._TEST_PROVIDER_VANITY_URL)
        
        experience_form = response.forms['continuing_education_form']
        experience_form['title'] = 'SomeEd'
        experience_form['year'] = '2008'
        experience_form.submit()

        # check again
        response = self.testapp.get('/provider/profile/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("<del>Remplissez votre CV</del>")


if __name__ == "__main__":
    unittest.main()
    
    
