# -*- coding: utf-8 -*-

from base import BaseTest
import unittest

class ProspectTest(BaseTest):

    def test_add_prospect(self):
        self.create_prospect()
        
        # hit up the prospect tour url
        response = self.testapp.get('/tour/103')
        
        # should be the tour page
        response.mustcontain("Improve your online presence")
        response.mustcontain("It's Who You Are!")
        
        # click on signup page
        response.mustcontain("/en/signup/provider")

        response = self.testapp.get('/en/signup/provider')

        # log in as admin and check the logs
        self.login_as_admin()
        response = self.testapp.get("/admin/prospects/103")
        
        response.mustcontain("/en/signup/provider")
        response.mustcontain("/tour/103")
        
    def test_add_prospect_language(self):
        self.create_prospect(prospect_language='fr')
        # hit up the prospect tour url
        response = self.testapp.get('/tour/103')
        
        # should be the tour page
        response.mustcontain("Améliorez votre présence en ligne avec un profil entièrement dédié aux soins de la santé.")
        response.mustcontain("C'est qui je suis!")
        response.mustcontain('/fr/signup/provider')

        # click on signup page
        response = self.testapp.get('/fr/signup/provider')

        # log in as admin and check the logs
        self.login_as_admin()
        response = self.testapp.get("/admin/prospects/103")
        
        response.mustcontain("/fr/signup/provider")
        response.mustcontain("/tour/103")
        
    def test_add_prospect_signup_page(self):
        self.create_prospect()
        
        # hit up the prospect signup url
        response = self.testapp.get('/signup/103')
        
        # should be the 2nd signup page (prepopulated)
        response.mustcontain("You are just one click away from having your own online presence.")
        response.mustcontain('<input id="first_name" name="first_name" type="hidden" value="%s">' % 'Al')
        response.mustcontain('<input id="last_name" name="last_name" type="hidden" value="%s">' % 'Swearingen')
        response.mustcontain('<option selected value="%s">' % 'doctor')
                        

    def test_add_prospect_blog_page(self):
        self.create_prospect()
        
        # hit up the prospect tour url
        response = self.testapp.get('/blog/103')
        
        # should be redirect to the blog page
        self.assertEqual(response.headers['Location'], "http://blog.veosan.com")
                
        # click on signup page
        response = self.testapp.get('/en/signup/provider')

        # log in as admin and check the logs
        self.login_as_admin()
        response = self.testapp.get("/admin/prospects/103")
        
        response.mustcontain("/en/signup/provider")
        response.mustcontain("<td>/blog/103</td>")

    def test_add_prospect_duplicate_id(self):
        self.create_prospect()
        self.login_as_admin()
        
        response = self.testapp.get('/admin/prospects')
        prospect_form = self.populate_prospect_form(response.forms['prospect_form'], 103)

        response = prospect_form.submit()
                
        response.mustcontain("Prospect ID is not unique")


    def test_add_prospect_signup_page_complete_process(self):
        self.create_prospect()
        
        # hit up the prospect signup url
        response = self.testapp.get('/signup/103')
        
        # should be the 2nd signup page (prepopulated)
        response.mustcontain("You are just one click away from having your own online presence.")
        response.mustcontain('<input id="first_name" name="first_name" type="hidden" value="%s">' % 'Al')
        response.mustcontain('<input id="last_name" name="last_name" type="hidden" value="%s">' % 'Swearingen')
        response.mustcontain('<option selected value="%s">' % 'doctor')
        
        signup_form = response.forms['provider_signup_form2']
        signup_form['password'] = self._TEST_PROVIDER_PASSWORD
        signup_form['password_confirm'] = self._TEST_PROVIDER_PASSWORD
        
        welcome_response = signup_form.submit().follow()
        
        # should be on the welcome page
        welcome_response.mustcontain("Welcome!")
        self.logout_provider(language='en')
        
        # recycle the signup URL
        response = self.testapp.get('/signup/103').follow()
        response.mustcontain(no="You are just one click away from having your own online presence.")
        response.mustcontain("Sign up below to get started today!")


    def test_invalid_prospect_code(self):
        self.create_prospect()
        
        # hit up the prospect signup url
        response = self.testapp.get('/signup/zzvzzt').follow()        
        
        # should be the 2nd signup page (prepopulated)
        response.mustcontain("Be Present")
        response.mustcontain("Before this, you didn't exist! Get a professional profile that sets you apart.")


        # hit up the prospect tour url
        response = self.testapp.get('/tour/zzvzzt')
        response.mustcontain("Improve your online presence with a profile focused on health care.")

        # hit up the prospect blog url, default sends to english blog
        response = self.testapp.get('/blog/zzvzzt')
        self.assertEqual(response.headers['Location'], "http://blog.veosan.com")

if __name__ == "__main__":
    unittest.main()
    
    
