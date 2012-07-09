from data import db
from wtforms import ValidationError

class UniqueVanityURL(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        vanity_url = field.data
    
        if vanity_url:
            # try to fetch a provider with this vanity URL
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            if provider:
                # taken
                raise ValidationError(self.message)
    
            else:
                #available
                pass
