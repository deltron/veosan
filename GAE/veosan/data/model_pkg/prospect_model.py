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


    # eventually link to a provider if they sign up
    #provider = ndb.KeyProperty(kind='Provider')
    
 
    def get_site_logs(self):
        return SiteLog.query(SiteLog.prospect == self.key).order(-SiteLog.access_time).fetch()
    
    def get_notes(self):
        return ProspectNote.query(ProspectNote.prospect == self.key).order(-ProspectNote.created_on).fetch()
    
    def get_blog_url(self):
        # Replace HOST for dev
        return 'http://veosan.com/blog/%s' % self.prospect_id

    def get_tour_url(self):
        # Replace HOST for dev
        return 'http://veosan.com/tour/%s' % self.prospect_id
    
    def get_signup_url(self):
        # Replace HOST for dev
        return 'http://veosan.com/signup/%s' % self.prospect_id