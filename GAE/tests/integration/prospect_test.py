# -*- coding: utf-8 -*-

from base import BaseTest
import unittest

class ProspectTest(BaseTest):
    def create_prospect(self, prospect_id = 103):
        self.login_as_admin()
        # create a new prospect
        response = self.testapp.get('/admin/prospects')
        prospect_form = self.populate_prospect_form(response.forms['prospect_form'], prospect_id)

        response = prospect_form.submit().follow()
        
        response.mustcontain("/admin/prospects/" + str(prospect_id))
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain("/admin/prospects/delete/" + str(prospect_id))
        
        self.logout_admin()
        
        
    def populate_prospect_form(self, prospect_form, prospect_id):
        prospect_form['prospect_id'] = prospect_id
        prospect_form['language'] = 'en'
        prospect_form['email'] = self._TEST_PROVIDER_EMAIL
        prospect_form['first_name'] = 'Al'
        prospect_form['last_name'] = 'Swearingen'
        prospect_form['category'] = 'doctor'
        return prospect_form

    def test_add_prospect(self):
        self.create_prospect()
        
        # hit up the prospect tour url
        response = self.testapp.get('/tour/103')
        
        # should be the tour page
        response.mustcontain("Improve your online presence")
        response.mustcontain("It's Who You Are!")
        
        # click on signup page
        response = self.testapp.get('/en/signup/provider')

        # log in as admin and check the logs
        self.login_as_admin()
        response = self.testapp.get("/admin/prospects/103")
        
        response.mustcontain("/en/signup/provider")
        response.mustcontain("/tour/103")
        
    def test_add_prospect_language(self):
        pass

    def test_add_prospect_signup_page(self):
        self.create_prospect()
        
        # hit up the prospect signup url
        response = self.testapp.get('/signup/103')
        
        # should be the 2nd signup page (prepopulated)
        response.mustcontain("You are just one click away from having your own online presence.")
        response.mustcontain('<input id="first_name" name="first_name" type="hidden" value="%s">' % 'Al')
        response.mustcontain('<input id="last_name" name="last_name" type="hidden" value="%s">' % 'Swearingen')
        response.mustcontain('<option selected value="%s">' % 'doctor')
                        

    def test_add_prospect_duplicate_id(self):
        self.create_prospect()
        self.login_as_admin()
        
        response = self.testapp.get('/admin/prospects')
        prospect_form = self.populate_prospect_form(response.forms['prospect_form'], 103)

        response = prospect_form.submit()
                
        response.mustcontain("Prospect ID is not unique")

if __name__ == "__main__":
    unittest.main()
    
    
