# -*- coding: utf-8 -*-

from base import BaseTest

class AuthenticationTest(BaseTest):
     
    def test_provider_login_success(self):
        self.create_complete_provider_profile()
        


    def test_provider_login_fail(self):
        self.create_complete_provider_profile()
        

    def test_admin_login_success(self):
        pass

    def test_admin_login_fail(self):
        pass