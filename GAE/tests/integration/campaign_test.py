# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

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
        
        
    def test_add_prospect_to_campaign(self):
        self.create_campaign()
        self.create_prospect('p123', 'fr')
        prospect = db.get_provider_prospect_from_email(self._TEST_PROVIDER_EMAIL)
        
        self.login_as_admin()
        campaign_admin_page = self.testapp.get('/admin/campaigns')
        details_page = campaign_admin_page.click(linkid='campaign-detail-link-1')
        prospect_modal_page = details_page.click(linkid='edit-prospects-link')
        prospect_form = prospect_modal_page.forms['edit_campaign_prospects_form']
        prospect_form['prospect'] = prospect.key.urlsafe()
        detail_page = prospect_form.submit()
        detail_page.mustcontain('p123')
        
    def test_remove_prospect_to_campaign(self):
        self.create_campaign()
        self.create_prospect('p123', 'fr')
        prospect = db.get_provider_prospect_from_email(self._TEST_PROVIDER_EMAIL)
        # add
        self.login_as_admin()
        campaign_admin_page = self.testapp.get('/admin/campaigns')
        details_page = campaign_admin_page.click(linkid='campaign-detail-link-1')
        prospect_modal_page = details_page.click(linkid='edit-prospects-link')
        prospect_form = prospect_modal_page.forms['edit_campaign_prospects_form']
        prospect_form['prospect'] = prospect.key.urlsafe()
        detail_page = prospect_form.submit()
        detail_page.mustcontain('p123')
        # remove
        prospect_modal_page = details_page.click(linkid='edit-prospects-link')
        prospect_form = prospect_modal_page.forms['edit_campaign_prospects_form']
        prospect_form['prospect'] = None
        detail_page = prospect_form.submit()
        detail_page.mustcontain('0 Campaign Prospects')
        
        
if __name__ == "__main__":
    unittest.main()
    
    
