'''
    database access
'''
#from google.appengine.ext import db as gdb
from google.appengine.ext import ndb
import logging
from datetime import datetime, date, time
from data.model import Booking, Patient, Provider, User
from handler.auth import PROVIDER_ROLE, PATIENT_ROLE
import db_util
  
def get_from_urlsafe_key(urlsafe_key):
    logging.info('(db.get_from_urlsafe_key) Getting from urlsafe key: %s' % urlsafe_key)
    key = ndb.Key(urlsafe=urlsafe_key)
    logging.info('(db.get_from_urlsafe_key) Getting kind: %s and key: %s' % (key.kind(), key.id()))
    return key.get()

def storeBooking(r, patient=None, provider=None):
    logging.info('Saving Booking from:' + str(r))
    booking = Booking()
    booking.requestCategory = r['category']
    booking.requestLocation = r['location']
    requestDateString = r['booking_date']
    requestTimeString = r['booking_time']
    requestDateTime = datetime.strptime(requestDateString + " " + requestTimeString, '%Y-%m-%d %H')
    booking.requestDateTime = requestDateTime
    booking.comments = r.get('comments', '')
    booking.patient = patient
    booking.provider = provider
    booking.put()
    return booking
    
def storePatient(r, user):
    # r is a MultiDict object from the request
    logging.info("Storing patient profile from request:" + str(r.__dict__))
    patient = Patient()
    # set all the properties
    db_util.set_all_properties_on_entity_from_multidict(patient, r)
    patient.user = user.key
    # store
    patient_key = patient.put()
    logging.info('Saved patient key:' + str(patient_key))
    logging.info(vars(patient))
    return patient


def fetchProviders():
    # TODO add limit
    providers = Provider.query().order(Provider.last_name)
    #gdb.GqlQuery("SELECT * from Provider ORDER BY last_name ASC LIMIT 50")
    return providers

def fetch_bookings():
    return Booking.query().order(-Booking.created_on)

def fetch_future_bookings(provider):
    yesterday_at_midnight = datetime.combine(date.today(), time())
    bookings = Booking.query(ancestor=provider.key).order(Booking.dateTime).fetch(50)
    #, Booking.dateTime > yesterday_at_midnight
    return bookings

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

def get_provider_from_resetpassword_key(resetpassword_key):
    provider = Provider.query(Provider.resetpassword_key == resetpassword_key).get()
    logging.debug('(db.get_provider_from_resetpassword_key) Found provider %s from resetpassword_key: %s' % (provider, resetpassword_key))
    return provider

def get_provider_from_activation_key(activation_key):
    provider = Provider.query(Provider.activation_key == activation_key).get()
    logging.debug('Found provider %s from activation_key: %s' % (provider, activation_key))
    return provider

def get_user_from_email(email):
    return User.query(User.auth_ids == email).get()

def get_user_roles(user):
    '''
        return roles from user based on link to provider or patient
    '''
    roles = []
    provider = Provider.query(Provider.user == user.key).get()
    if provider:
        roles.append(PROVIDER_ROLE)
    patient = Patient.query(Patient.user == user.key).get()
    if patient:
        roles.append(PATIENT_ROLE)
    return roles

def get_user_profiles(user):
    '''
        return profiles from user based on link to provider or patient
    '''
    profiles = []
    providers = Provider.query(Provider.user == user.key)
    for pro in providers:
        profiles.append(pro)
    patients = Patient.query(Patient.user == user.key)
    for pat in patients:
        profiles.append(pat)
    return profiles

def get_provider_profile(user):
    '''returns the first provider profile liked to user. Returns None if user is not a provider'''
    if user:
        return Provider.query(Provider.user == user.key).get()
    else:
        return None
    
def get_patient_profile(user):
    '''returns the first patient profile liked to user. Returns None if user is not a patient'''
    if user:
        return Patient.query(Patient.user == user.key).get()
    else:
        return None
    
    