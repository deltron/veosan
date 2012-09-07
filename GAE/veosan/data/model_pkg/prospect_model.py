from google.appengine.ext import ndb
from data.model_pkg.site_model import SiteLog

class ProviderProspect(ndb.Model):
    # address from AppEngine
    gae_country = ndb.StringProperty()
    gae_region = ndb.StringProperty()
    gae_city = ndb.StringProperty()
    gae_city_lat_long = ndb.StringProperty()
    
    # unique ID / url for this prospect
    prospect_id = ndb.StringProperty()
    prospect_email = ndb.StringProperty()
    prospect_landing = ndb.StringProperty()

    landing_hits = ndb.IntegerProperty(default=0)


    # eventually link to a provider if they sign up
    #provider = ndb.KeyProperty(kind='Provider')
    
 
    def get_site_logs(self):
        return SiteLog.query(SiteLog.prospect == self.key).order(-SiteLog.access_time).fetch()
        