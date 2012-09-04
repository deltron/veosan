'''
    database access
'''
#from google.appengine.ext import db as gdb
from google.appengine.ext import ndb, db as gdb
import logging
from datetime import datetime, date, time
from data.model import Booking, Patient, User, SiteConfig, LogEvent, SiteCounter,\
    PartialProvider
from data.model_pkg.network_model import Invite, ProviderNetworkConnection
from data.model_pkg.provider_model import Provider
import utilities
  
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


def create_patient_from_provider(provider):
    new_patient = Patient()
    new_patient.first_name = provider.first_name
    new_patient.last_name = provider.last_name
    new_patient.address = provider.address
    new_patient.city = provider.city
    new_patient.email = provider.email
    new_patient.postal_code = provider.postal_code
    new_patient.province = provider.province
    new_patient.telephone = provider.phone
    new_patient.terms_agreement = True
    new_patient.user = provider.user
    new_patient_key = new_patient.put()
    return new_patient


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

def get_partial_provider_from_email(email):
    return PartialProvider.query(PartialProvider.email == email).get()

def get_patient_from_email(email):
    return Patient.query(Patient.email == email).get()

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

def get_site_counter():
    site_counter = SiteCounter.query().get()
    if site_counter == None:
        site_counter = SiteCounter()
        site_counter.put()
    
    return site_counter
        

def store(key, form, data):
    # data is a MultiDict object from the request
    logging.info("Storing on key:%s with data:%s" % (key, str(data)))
    datastore_object = get_from_urlsafe_key(key)
    # set all the properties
    form.populate_obj(datastore_object)
    # store
    datastore_object.put()
    

def get_provider_network_connection(source_key, target_key):
    return ProviderNetworkConnection.query(ProviderNetworkConnection.source_provider == source_key, ProviderNetworkConnection.target_provider == target_key).get()
    
def get_schedule_for_date_time(provider, book_date, book_time):
    book_weekday_index = datetime.strptime(book_date, '%Y-%m-%d').weekday()
    (book_weekday_key, book_weekday_label) = utilities.time.get_day_of_the_week_from_python_weekday(book_weekday_index)
    book_time_int = int(book_time)
    
    schedules = provider.get_schedules()
    for schedule in schedules:
        if book_weekday_key == schedule.day:
            if book_time_int >= schedule.start_time and book_time_int <= schedule.end_time:
                return schedule


