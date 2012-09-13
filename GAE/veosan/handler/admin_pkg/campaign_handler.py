from handler.auth import admin_required
from handler.admin import AdminBaseHandler
from forms.campaign import CampaignForm
from data.model_pkg.campaign_model import EmailCampaign
from data import db

class AdminCampaignsHandler(AdminBaseHandler):
    
    def render_campaigns(self, add_campaign_form=None):
        campaigns = db.fetch_campaigns()
        if add_campaign_form is None:
            add_campaign_form = CampaignForm().get_form()
        self.render_template('admin/admin_campaigns.html', campaigns=campaigns, add_campaign_form=add_campaign_form) 
    
    @admin_required
    def get(self):
        self.render_campaigns()

    def post(self):
        add_campaign_form = CampaignForm().get_form(self.request.POST)
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
    @admin_required
    def get(self, campaign_key):
        campaign = db.get_from_urlsafe_key(campaign_key)
        self.render_template('admin/campaign_details.html', campaxxign=campaign)
