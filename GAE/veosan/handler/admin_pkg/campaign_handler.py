from handler.auth import admin_required
from handler.admin import AdminBaseHandler
from forms.campaign import AddCampaignForm, EditCampaignForm
from data.model_pkg.campaign_model import Campaign
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
            campaign = Campaign()
            add_campaign_form.populate_obj(campaign)
            campaign.put()
            self.redirect("/admin/campaigns")
        else:
            self.render_campaign(add_campaign_form=add_campaign_form)
    


class AdminCampaignDeleteHandler(AdminBaseHandler):
    @admin_required
    def get(self, campaign_key):
        campaign = db.get_from_urlsafe_key(campaign_key)
        if campaign and isinstance(campaign, Campaign):
            campaign.key.delete()
        # back to campaign admin page
        self.redirect('/admin/campaigns', success_message='Campaign created!')


class AdminCampaignDetailsHandler(AdminBaseHandler):
    
    def render_campaign_details(self, campaign, edit_campaign_form=None, **kw):
        if not edit_campaign_form:
            edit_campaign_form = EditCampaignForm().get_form(obj=campaign)
        all_prospects = db.fetch_prospects()
        self.render_template('admin/campaign_details.html', campaign=campaign, edit_campaign_form=edit_campaign_form, all_prospects=all_prospects, **kw)
        
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
            self.render_campaign_details(campaign, success_message='Campaign saved!')
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
        
    def display_single_email_get(self, campaign_key, prospect_id):
        campaign = db.get_from_urlsafe_key(campaign_key)
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        logging.info('Displaying Email for prospect %s' % prospect)
        if prospect:
            self.render_campaign_details(campaign, prospect=prospect, show_modal='email')
        else:
            self.render_campaign_details(campaign, error_message='Prospect not found')
        
    def mark_as_sent_get(self, campaign_key, prospect_id):
        campaign = db.get_from_urlsafe_key(campaign_key)
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        logging.info('Marking email as sent for prospect %s' % prospect)
        if prospect:
                
            self.render_campaign_details(campaign, prospect=prospect, show_modal='email')
        else:
            self.render_campaign_details(campaign, error_message='Prospect not found')
                    

def generate_prospect_email_dict(prospect, host):
    email_dict = {}
    email_dict['name'] = prospect.first_name
    email_dict['first_name'] = prospect.first_name
    email_dict['last_name'] = prospect.last_name
    email_dict['language'] = prospect.language
    email_dict['email'] = prospect.email
    #email_dict['category'] = prospect.category  # format to English or French string
    email_dict['blog_url'] = prospect.get_blog_url(host)
    email_dict['signup_url'] = prospect.get_signup_url(host)
    email_dict['tour_url'] = prospect.get_tour_url(host)                              
    return email_dict
