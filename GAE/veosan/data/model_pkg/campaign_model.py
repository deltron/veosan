from google.appengine.ext import ndb

class EmailCampaign(ndb.Model):
    
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    
    # unique name this prospect
    name = ndb.StringProperty()
    
    subject_fr = ndb.StringProperty()
    body_fr = ndb.TextProperty()
    
    subject_en = ndb.StringProperty()
    body_en = ndb.TextProperty()
    
    prospects = ndb.KeyProperty(repeated=True)
    