# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db
from data.model import User

class LanguageTest(BaseTest):
    def test_switch_language_on_contact_form(self):
        # default language should be french
        contact_page = self.testapp.get("/contact")
        contact_page.mustcontain("Nous voulons savoir")
        contact_page.mustcontain("Sujet")
        contact_page.mustcontain("Adresse courriel")
        contact_page.mustcontain("Envoyer")
        
        # switch from default french to english
        language_switch = self.testapp.get("/lang/en")
        contact_page_en = language_switch.follow()
        
        # no referer in header so manually go back to contact page
        contact_page_en = self.testapp.get("/contact")
        
        # will be redirected back to contact page
        contact_page_en.mustcontain("We want to know")
        contact_page_en.mustcontain("Subject")
        contact_page_en.mustcontain("E-mail Address")
        contact_page_en.mustcontain("Send")
        
        

if __name__ == "__main__":
    unittest.main()
    
    
