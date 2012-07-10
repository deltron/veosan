# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class PublicProfileTest(BaseTest):
    
    def test_visit_public_profile(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        

    

if __name__ == "__main__":
    unittest.main()
    
    
