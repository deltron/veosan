from google.appengine.ext import ndb
from data.model_pkg.prospect_model import ProspectNote

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
    
    