from google.appengine.ext import ndb



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
    