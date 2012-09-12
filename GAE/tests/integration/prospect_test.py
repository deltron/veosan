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

    def test_add_prospect_underscore(self):
        self.login_as_admin()
        
        # create a new prospect
        
        response = self.testapp.get('/admin/prospects')
        
        prospect_form = response.forms['prospect_form']
        prospect_form['prospect_id'] = 'tour_underscore'
        prospect_form['prospect_email'] = self._TEST_PROVIDER_EMAIL
        prospect_form['prospect_landing'] = '/en/tour'

        response = prospect_form.submit().follow()
        
        response.mustcontain("http://veosan.com/p/tour_underscore")
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain("/admin/prospects/tour_underscore")
        
        self.logout_admin()
        
        # hit up the prospect url
        response = self.testapp.get('/p/tour_underscore').follow()
        
        # should be the tour page
        response.mustcontain("Improve your online presence")
        response.mustcontain("It's Who You Are!")
        
        # click on signup page
        response = self.testapp.get('/en/signup/provider')

        # log in as admin and check the logs
        self.login_as_admin()
        response = self.testapp.get("/admin/prospects/tour_underscore")
        
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


    def test_add_prospect_duplicate_email(self):
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
        prospect_form['prospect_id'] = 104
        prospect_form['prospect_email'] = self._TEST_PROVIDER_EMAIL
        prospect_form['prospect_landing'] = '/en/signup/provider'

        response = prospect_form.submit().follow()
        
        response.mustcontain("http://veosan.com/p/103")
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain("/admin/prospects/103")

        response.mustcontain("http://veosan.com/p/104")
        response.mustcontain(self._TEST_PROVIDER_EMAIL)
        response.mustcontain("/admin/prospects/104")
        
        
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

        self.logout_admin()
        
        # hit up the prospect url
        response = self.testapp.get('/p/104').follow()
        
        # should be the tour page
        response.mustcontain("Before this, you didn't exist!")

        response = self.testapp.get("/en/tour")
        response.mustcontain("It's Who You Are!")
        
        # click on signup page
        response = self.testapp.get('/en/signup/provider')

        # log in as admin and check the logs
        self.login_as_admin()
        response = self.testapp.get("/admin/prospects/104")
        
        response.mustcontain("/en/signup/provider")
        response.mustcontain("/en/tour")


if __name__ == "__main__":
    unittest.main()
    
    
