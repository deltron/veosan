from google.appengine.ext import ndb
from data.model_pkg.site_model import SiteLog
import util
from data.model_pkg.provider_model import Provider


class ProspectNote(ndb.Model):
    prospect = ndb.KeyProperty(kind='ProviderProspect')

    body = ndb.TextProperty()
    note_type = ndb.StringProperty(choices=util.note_types) 
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty()
    event_date = ndb.DateTimeProperty(auto_now_add=True)
    campaign = ndb.KeyProperty(kind='Campaign')
    


class ProviderProspect(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)

    # address from AppEngine
    gae_country = ndb.StringProperty()
    gae_region = ndb.StringProperty()
    gae_city = ndb.StringProperty()
    gae_city_lat_long = ndb.StringProperty()
    
    # unique ID / url for this prospect
    prospect_id = ndb.StringProperty()
    language = ndb.StringProperty()
    email = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    category = ndb.StringProperty()

    landing_hits = ndb.IntegerProperty(default=0)

    # prospect status
    tags = ndb.StringProperty(repeated=True)
    employment_tags = ndb.StringProperty(repeated=True)

    def get_provider(self):
        return Provider.query(Provider.email == self.email).get()
 
    def get_site_logs(self):
        return SiteLog.query(SiteLog.prospect == self.key).order(-SiteLog.access_time).fetch()
    
    def get_last_site_visit_timestamp(self):
        latest_site_visit = SiteLog.query(SiteLog.prospect == self.key).order(-SiteLog.access_time).get()
        if latest_site_visit:
            return latest_site_visit.access_time
        else:
            return None

    def get_notes(self):
        return ProspectNote.query(ProspectNote.prospect == self.key).order(-ProspectNote.event_date, -ProspectNote.created_on).fetch()
    
    def get_last_note_timestamp(self):
        latest_prospect_note = ProspectNote.query(ProspectNote.prospect == self.key).order(-ProspectNote.event_date).get()
        if latest_prospect_note:
            return latest_prospect_note.event_date
        else:
            return None

    def get_notes_count(self):
        return ProspectNote.query(ProspectNote.prospect == self.key).count()

    def get_notes_info_count(self):
        return ProspectNote.query(ProspectNote.prospect == self.key, ProspectNote.note_type == 'info').count()

    def get_notes_meeting_count(self):
        return ProspectNote.query(ProspectNote.prospect == self.key, ProspectNote.note_type == 'meeting').count()

    def get_notes_email_count(self):
        return ProspectNote.query(ProspectNote.prospect == self.key, ProspectNote.note_type == 'email').count()

    def get_notes_call_count(self):
        return ProspectNote.query(ProspectNote.prospect == self.key, ProspectNote.note_type == 'call').count()
    
    def get_campaigns(self):
        return Campaign.query(Campaign.prospects == self.key).order(-Campaign.created_on).fetch()
    
    def get_email_notes_for_campaign(self, campaign):
        notes_query = ProspectNote.query(ProspectNote.prospect == self.key, ProspectNote.campaign == campaign.key, ProspectNote.note_type == 'email')
        notes_query = notes_query.order(-ProspectNote.event_date, -ProspectNote.created_on)
        return notes_query.fetch()
    
    def get_email_notes_for_campaign_count(self, campaign):
        return ProspectNote.query(ProspectNote.prospect == self.key, ProspectNote.campaign == campaign.key, ProspectNote.note_type == 'email').count()
    
    def is_campaign_email_sent(self, campaign):
        return self.get_email_notes_for_campaign_count(campaign)
    
    def get_last_campaign_email_note_timestamp(self, campaign):
        notes_query = ProspectNote.query(ProspectNote.prospect == self.key, ProspectNote.campaign == campaign.key, ProspectNote.note_type == 'email')
        notes_query = notes_query.order(-ProspectNote.event_date, -ProspectNote.created_on)
        campaign_email = notes_query.get()
        if campaign_email:
            return campaign_email.event_date
        else:
            return None
    
    def get_blog_url(self, host):
        return 'http://%s/blog/%s' %  (host, self.prospect_id)

    def get_tour_url(self, host):
        return 'http://%s/tour/%s' %  (host, self.prospect_id)
    
    def get_signup_url(self, host):
        return 'http://%s/signup/%s' % (host, self.prospect_id)
    
    
    
#############################
# Campaign
#############################    

class Campaign(ndb.Model):
    # creation date
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    # unique name this prospect
    name = ndb.StringProperty()
    description = ndb.StringProperty()
    # Email Template - Francais
    subject_fr = ndb.StringProperty()
    body_fr = ndb.TextProperty()
    # Email Temaplte - English
    subject_en = ndb.StringProperty()
    body_en = ndb.TextProperty()
    # list of prospects
    prospects = ndb.KeyProperty(kind='ProviderProspect', repeated=True)

    ########################
    # Notes
    ########################
    def get_email_notes_count(self):
        return ProspectNote.query(ProspectNote.campaign == self.key, ProspectNote.note_type == 'email').count() 