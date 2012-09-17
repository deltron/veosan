from google.appengine.ext import ndb

class EmailCampaign(ndb.Model):
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
    prospects = ndb.KeyProperty(repeated=True)
    