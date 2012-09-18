from handler.auth import admin_required
from handler.admin import AdminBaseHandler
from forms.campaign import AddCampaignForm, EditCampaignForm
from data.model_pkg.campaign_model import EmailCampaign
from data import db
import logging
from google.appengine.ext import ndb

class AdminCampaignsHandler(AdminBaseHandler):
    
    def render_campaigns(self, add_campaign_form=None):
        campaigns = db.fetch_campaigns()
        if add_campaign_form is None:
            add_campaign_form = AddCampaignForm().get_form()
        self.render_template('admin/admin_campaigns.html', campaigns=campaigns, add_campaign_form=add_campaign_form) 
    
    @admin_required
    def get(self):
        self.render_campaigns()

    def post(self):
        add_campaign_form = AddCampaignForm().get_form(self.request.POST)
        if add_campaign_form.validate():
            campaign = EmailCampaign()
            add_campaign_form.populate_obj(campaign)
            campaign.put()
            self.redirect("/admin/campaigns")
        else:
            self.render_campaign(add_campaign_form=add_campaign_form)
    


class AdminCampaignDeleteHandler(AdminBaseHandler):
    @admin_required
    def get(self, campaign_key):
        campaign = db.get_from_urlsafe_key(campaign_key)
        if campaign and isinstance(campaign, EmailCampaign):
            campaign.key.delete()
        # back to campaign admin page
        self.redirect('/admin/campaigns')


class AdminCampaignDetailsHandler(AdminBaseHandler):
    
    def render_campaign_details(self, campaign, edit_campaign_form=None):
        if not edit_campaign_form:
            edit_campaign_form = EditCampaignForm().get_form(obj=campaign)
        all_prospects = db.fetch_prospects()
        self.render_template('admin/campaign_details.html', campaign=campaign, edit_campaign_form=edit_campaign_form, all_prospects=all_prospects)
        
    @admin_required
    def get(self, campaign_key):
        ''' Display Campaign details '''
        campaign = db.get_from_urlsafe_key(campaign_key)
        # split this out into Edit handler with paging
        self.render_campaign_details(campaign)

    def post(self, campaign_key):
        ''' Edit Campaign Info '''
        campaign = db.get_from_urlsafe_key(campaign_key)
        edit_campaign_form = EditCampaignForm().get_form(self.request.POST)
        if edit_campaign_form.validate():
            edit_campaign_form.populate_obj(campaign)
            campaign.put()
            self.render_campaign_details(campaign)
        else:
            self.render_campaign_details(campaign, edit_campaign_form=edit_campaign_form)       
        
    def edit_prospects_post(self, campaign_key):
        '''
            Handle POST form edit prospects modal window
        '''
        campaign = db.get_from_urlsafe_key(campaign_key)
        prospect_urlsafe_keys = self.request.get_all('prospect')
        prospect_keys = map(lambda usk: ndb.Key(urlsafe=usk), prospect_urlsafe_keys)
        logging.info('Setting prospects count %s' % len(prospect_keys))
        campaign.prospects = prospect_keys
        campaign.put() 
        self.render_campaign_details(campaign=campaign)
        
    def generate_emails_get(self, campaign_key):
        ''' generate emails from prospect list'''
        campaign = db.get_from_urlsafe_key(campaign_key)
        self.render_template('admin/campaign_email.html', campaign=campaign)
        

def generate_prospect_email_dict(prospect):
    email_dict = {}
    email_dict['name'] = prospect.first_name
    email_dict['first_name'] = prospect.first_name
    email_dict['last_name'] = prospect.last_name
    email_dict['language'] = prospect.language
    email_dict['email'] = prospect.email
    email_dict['blog_url'] = prospect.get_blog_url()
    return email_dict