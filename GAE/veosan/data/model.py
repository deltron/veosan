from google.appengine.ext import ndb
import logging
from webapp2_extras.appengine.auth.models import User as Webapp2AuthUser
import util
from datetime import datetime
from data.model_pkg.booking_schedule_model import Booking

'''
    stored data 
'''



class PartialProvider(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    gae_country = ndb.StringProperty()
    gae_region = ndb.StringProperty()
    gae_city = ndb.StringProperty()
    gae_city_lat_long = ndb.StringProperty()

class User(Webapp2AuthUser):
    '''
        Extending the Webapp2 Auth User to add roles
    '''
    roles = ndb.StringProperty(repeated=True)
    
    signup_token = ndb.StringProperty()
    resetpassword_token = ndb.StringProperty()
    claim_url = ndb.StringProperty()
    
    confirmed = ndb.BooleanProperty()

    language = ndb.StringProperty(default='en')
    
    last_login = ndb.DateTimeProperty()

    def get_email(self):
        return self.auth_ids[0]
    
    def is_activated_and_has_password(self):
        return (self.password != None) & (self.signup_token == None)

'''
    @classmethod
    def create_token(cls, user_id, subject):
        entity = cls.token_model.create(user_id, subject)
        return entity.token

    @classmethod
    def validate_token(cls, user_id, token, subject):
        return cls.validate_token(user_id, subject, token)

    @classmethod
    def delete_token(cls, user_id, token, subject):
        cls.token_model.get_key(user_id, subject, token).delete()
'''

class Patient(ndb.Model):
    '''
    A patient
    '''
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.KeyProperty(kind=User)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    terms_agreement = ndb.BooleanProperty()
    
    # address from AppEngine
    gae_country = ndb.StringProperty()
    gae_region = ndb.StringProperty()
    gae_city = ndb.StringProperty()
    gae_city_lat_long = ndb.StringProperty()
    
    # Address for homecare
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    postal_code = ndb.StringProperty()
    province = ndb.StringProperty()
    
    def get_bookings(self):
        return Booking.query(Booking.patient == self.key).fetch()
    
    def get_future_bookings(self):
        return Booking.query(Booking.patient == self.key, Booking.datetime >= datetime.now()).fetch()
    
    def get_future_unconfirmed_bookings(self):
        return Booking.query(Booking.patient == self.key, Booking.datetime >= datetime.now(), Booking.confirmed==False).fetch()



class LogEvent(ndb.Model):
    user = ndb.KeyProperty(kind=User)
    admin = ndb.BooleanProperty(default=False)

    created_on = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.StringProperty()
    referer = ndb.TextProperty()



