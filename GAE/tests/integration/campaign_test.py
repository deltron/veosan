# -*- coding: utf-8 -*-

from base import BaseTest
import unittest

class CampaignTest(BaseTest):
    
    def create_campaign(self, prospect_id = 103, prospect_language = 'en'):
        self.login_as_admin()
        # create a new prospect
        response = self.testapp.get('/admin/campaigns')
        add_form = response.forms['campaign_form']
        add_form['name'] = "Brand New Test Campaign"
        response = add_form.submit().follow()
        response.mustcontain("Brand New Test Campaign")
        self.logout_admin()
        


    def test_add_campaign(self):
        self.create_campaign()
        
        self.login_as_admin()
        campaign_admin_page = self.testapp.get('/admin/campaigns')
        # check details page
        details_page = campaign_admin_page.click(linkid='campaign-detail-link-1')
        details_page.mustcontain("Brand New Test Campaign")
        details_page.mustcontain("Campaign Prospects")
        details_page.mustcontain("Email Templates")
        self.logout_admin()
        
    
if __name__ == "__main__":
    unittest.main()
    
    
