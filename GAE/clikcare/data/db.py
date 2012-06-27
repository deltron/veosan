'''
    database access
'''
#from google.appengine.ext import db as gdb
from google.appengine.ext import ndb
import logging
from datetime import datetime, date, time
from data.model import Booking, Patient, Provider, User
import db_util
  
def get_from_urlsafe_key(urlsafe_key):
    logging.info('(db.get_from_urlsafe_key) Getting from urlsafe key: %s' % urlsafe_key)
    key = ndb.Key(urlsafe=urlsafe_key)
    logging.info('(db.get_from_urlsafe_key) Getting kind: %s and key: %s' % (key.kind(), key.id()))
    return key.get()

def storeBooking(r, patient=None, provider=None):
    logging.info('Saving Booking from:' + str(r))
    booking = Booking()
    booking.request_category = r['category']
    booking.request_location = r['location']
    requestDateString = r['booking_date']
    requestTimeString = r['booking_time']
    request_datetime = datetime.strptime(requestDateString + " " + requestTimeString, '%Y-%m-%d %H')
    booking.request_datetime = request_datetime
    booking.request_homecare = r.has_key('homecare')
    booking.comments = r.get('comments', '')
    booking.patient = patient
    booking.provider = provider
    booking.put()
    return booking
    
def store_patient(r):
    # r is a MultiDict object from the request
    logging.info("Storing patient profile from request:" + str(r.__dict__))
    patient = Patient()
    
    # set all the properties
    db_util.set_all_properties_on_entity_from_multidict(patient, r)

    # store
    patient.put()
    logging.info('Saved patient:' + str(patient.email))
    logging.info(vars(patient))
    return patient

def fetch_patients():
    return Patient.query().order(Patient.last_name)

def fetch_providers():
    return Provider.query().order(Provider.last_name)

def fetch_bookings():
    return Booking.query().order(-Booking.created_on)

def get_bookings_for_patient(patient):
    return Booking.query(Booking.patient == patient.key).fetch()

def initProvider(provider_email):
    ''' inititalize provider with email. return the provider's key '''
    new_provider = Provider()
    new_provider.email = provider_email
    new_provider.enable = True
    provider_key = new_provider.put()
    return provider_key

def getProvider(request):
    ''' get provider from a request dict, key = provider_key'''
    return get_from_urlsafe_key(request.get('provider_key'))
    
def getOrCreateProvider(provider_key):
    if (provider_key):
        logging.info('Getting existing provider with key:' + provider_key)
        provider = get_from_urlsafe_key(provider_key)
    else:
        logging.info('Creating new provider')
        provider = Provider()
    return provider


def storeProvider(r):
    # r is a MultiDict object from the request
    logging.info("Storing provider profile from request:" + str(r.__dict__))
    provider = getOrCreateProvider(r['provider_key'])
    
    # set all the properties
    db_util.set_all_properties_on_entity_from_multidict(provider, r)
    
    # store
    provider_key = provider.put()
    logging.info('Saved provider key:' + str(provider_key))
    logging.info(vars(provider))
    return provider_key


def get_provider_from_email(email):
    provider = Provider.query(Provider.email == email).get()
    logging.debug('Provider for email %s is %s' % (email, provider))
    return provider   


def get_user_from_email(email):
    return User.query(User.auth_ids == email).get()

def get_user_from_signup_token(token):
    return User.query(User.signup_token == token).get()

def get_user_from_resetpassword_token(token):
    return User.query(User.resetpassword_token == token).get()

def get_provider_from_user(user):
    '''returns the first provider profile liked to user. Returns None if user is not a provider'''
    if user:
        return Provider.query(Provider.user == user.key).get()
    else:
        return None  
    
def get_patient_from_user(user):
    '''returns the first patient profile liked to user. Returns None if user is not a patient'''
    if user:
        return Patient.query(Patient.user == user.key).get()
    else:
        return None
    
    