from google.appengine.ext import ndb
from data.model_pkg.site_model import SiteLog
import util

class ProspectNote(ndb.Model):
    prospect = ndb.KeyProperty(kind='ProviderProspect')

    body = ndb.TextProperty()
    note_type = ndb.StringProperty(choices=util.note_types) 
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty()
    event_date = ndb.DateProperty(auto_now_add=True)
    


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

    # eventually link to a provider if they sign up
    #provider = ndb.KeyProperty(kind='Provider')
    
 
    def get_site_logs(self):
        return SiteLog.query(SiteLog.prospect == self.key).order(-SiteLog.access_time).fetch()
    
    def get_last_site_visit_timestamp(self):
        latest_site_visit = SiteLog.query(SiteLog.prospect == self.key).order(-SiteLog.access_time).get()
        if latest_site_visit:
            return latest_site_visit.access_time
        else:
            return None

    def get_notes(self):
        return ProspectNote.query(ProspectNote.prospect == self.key).order(-ProspectNote.created_on).fetch()

    def get_last_note_timestamp(self):
        latest_prospect_note = ProspectNote.query(ProspectNote.prospect == self.key).order(-ProspectNote.created_on).get()
        if latest_prospect_note:
            return latest_prospect_note.created_on
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
    
    def get_blog_url(self, host):
        return 'http://%s/blog/%s' %  (host, self.prospect_id)

    def get_tour_url(self, host):
        return 'http://%s/tour/%s' %  (host, self.prospect_id)
    
    def get_signup_url(self, host):
        return 'http://%s/signup/%s' % (host, self.prospect_id)