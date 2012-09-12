# -*- coding: utf-8 -*-

from base import BaseTest
import unittest

class ProspectTest(BaseTest):

    def test_add_prospect(self):
        self.login_as_admin()
        
        # create a new prospect
        
        response = self.testapp.get('/admin/prospects')
        
        prospect_form = response.forms['prospect_form']
        prospect_form['prospect_id'] = 103
        prospect_form['prospect_email'] = self._TEST_PROVIDER_EMAIL
        prospect_form['prospect_landing'] = '/en/tour'

        response = prospect_form.submit().follow()
        
        response.mustcontain("http://veosan.com/p/103")
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain("/admin/prospects/103")
        
        self.logout_admin()
        
        # hit up the prospect url
        response = self.testapp.get('/p/103').follow()
        
        # should be the tour page
        response.mustcontain("Improve your online presence")
        response.mustcontain("It's Who You Are!")
        
        # click on signup page
        response = self.testapp.get('/en/signup/provider')

        # log in as admin and check the logs
        self.login_as_admin()
        response = self.testapp.get("/admin/prospects/103")
        
        response.mustcontain("/en/signup/provider")
        response.mustcontain("/en/tour")



    def test_add_prospect_duplicate_id(self):
        self.login_as_admin()
        
        # create a new prospect
        
        response = self.testapp.get('/admin/prospects')
        
        prospect_form = response.forms['prospect_form']
        prospect_form['prospect_id'] = 103
        prospect_form['prospect_email'] = self._TEST_PROVIDER_EMAIL
        prospect_form['prospect_landing'] = '/en/tour'

        response = prospect_form.submit().follow()
        
        response.mustcontain("http://veosan.com/p/103")
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain("/admin/prospects/103")

        response = self.testapp.get('/admin/prospects')
        
        prospect_form = response.forms['prospect_form']
        prospect_form['prospect_id'] = 103
        prospect_form['prospect_email'] = self._TEST_PROVIDER_EMAIL
        prospect_form['prospect_landing'] = '/en/tour'

        response = prospect_form.submit()
        
        response.mustcontain("Prospect ID is not unique")


if __name__ == "__main__":
    unittest.main()
    
    
