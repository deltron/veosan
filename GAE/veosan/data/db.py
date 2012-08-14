'''
    database access
'''
#from google.appengine.ext import db as gdb
from google.appengine.ext import ndb, db as gdb
import logging
from datetime import datetime, date, time
from data.model import Booking, Patient, Provider, User, SiteConfig, LogEvent,\
    Invite
  
def get_from_urlsafe_key(urlsafe_key):
    logging.info('(db.get_from_urlsafe_key) Getting from urlsafe key: %s' % urlsafe_key)
    key = ndb.Key(urlsafe=urlsafe_key)
    logging.info('(db.get_from_urlsafe_key) Getting kind: %s and key: %s' % (key.kind(), key.id()))
    return key.get()

def storeBooking(r, patient=None, provider=None):
    logging.info('Saving Booking from:' + str(r))
    booking = Booking()
    booking.booking_source = 'search'
    booking.request_category = r['category']
    booking.request_location = r['location']
    request_date = r['booking_date']
    request_time = r['booking_time']
    request_datetime = datetime.strptime(request_date + " " + request_time, '%Y-%m-%d %H')
    booking.request_datetime = request_datetime
    booking.request_homecare = r.has_key('homecare')
    booking.comments = r.get('comments', '')
    booking.patient = patient
    booking.provider = provider
    booking.put()
    return booking
    
def store_patient(r, form):
    # r is a MultiDict object from the request
    logging.info("Storing patient profile from request:" + str(r.__dict__))
    patient = Patient()
    
    # set all the properties
    form.populate_obj(patient)

    # store
    patient.put()
    logging.info('Saved patient:' + str(patient.email))
    logging.info(vars(patient))
    return patient

def fetch_patients():
    return Patient.query().order(Patient.last_name)

def fetch_invites():
    return Invite.query().order(-Invite.created_on)

def fetch_providers():
    return Provider.query().order(Provider.last_name)

def fetch_bookings():
    return Booking.query().order(-Booking.created_on)

def get_bookings_for_patient(patient):
    return Booking.query(Booking.patient == patient.key).fetch()

def init_provider(provider_email, vanity_url):
    ''' inititalize provider with email. return the provider's key '''
    new_provider = Provider()
    new_provider.email = provider_email
    new_provider.vanity_url = vanity_url
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


def storeProvider(provider=None, r=None, form=None):
    # r is a MultiDict object from the request
    logging.info("Storing provider profile from request:" + str(r.__dict__))
    if provider == None:
        provider = getOrCreateProvider(r['provider_key'])
    
    # set all the properties
    form.populate_obj(provider)
    
    # store
    provider_key = provider.put()
    logging.info('Saved provider key:' + str(provider_key))
    return provider_key


def get_provider_from_email(email):
    provider = Provider.query(Provider.email == email).get()
    logging.debug('Provider for email %s is %s' % (email, provider))
    return provider   

def get_all_vanity_urls():
    return Provider.query().fetch(projection=['vanity_url'])

def get_user_from_email(email):
    return User.query(User.auth_ids == email).get()

def get_user_from_signup_token(token):
    return User.query(User.signup_token == token).get()

def get_user_from_resetpassword_token(token):
    return User.query(User.resetpassword_token == token).get()

def get_invite_from_token(token):
    return Invite.query(Invite.token == token).get()

def get_invite_from_email(email):
    return Invite.query(Invite.email == email).get()


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
    
def get_provider_from_vanity_url(vanity_url):
    '''returns the first provider profile liked to vanity_url. Returns None if vanity_url is not provided '''
    if vanity_url:
        return Provider.query(Provider.vanity_url == vanity_url).get()
    else:
        return None  

def get_provider_from_domain(domain):
    '''returns the first provider profile liked to domain. Returns None if domain is not provided '''
    if domain:
        return Provider.query(Provider.vanity_domain == domain).get()
    else:
        return None  


def get_events_for_user(user):
    ''' returns all the log events for a user '''
    if user:
        return LogEvent.query(LogEvent.user == user.key).order(-LogEvent.created_on).fetch()
    else:
        return None  

def get_events_all():
    ''' returns all the log events '''
    return LogEvent.query().order(-LogEvent.created_on).fetch()


def get_site_config():
    return SiteConfig.query().get()

def store(key, form, data):
    # data is a MultiDict object from the request
    logging.info("Storing on key:%s with data:%s" % (key, str(data)))
    datastore_object = get_from_urlsafe_key(key)
    # set all the properties
    form.populate_obj(datastore_object)
    # store
    datastore_object.put()
    