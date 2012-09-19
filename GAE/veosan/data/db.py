'''
    database access
'''
#from google.appengine.ext import db as gdb
from google.appengine.ext import ndb
import logging
from datetime import datetime
from data.model import Booking, Patient, User, PartialProvider, LogEvent
from data.model_pkg.network_model import Invite, ProviderNetworkConnection
from data.model_pkg.provider_model import Provider
import utilities
from data.model_pkg.prospect_model import ProviderProspect
from data.model_pkg.campaign_model import EmailCampaign
from data.model_pkg.site_model import SiteCounter, SiteConfig, SiteLog
  
def get_from_urlsafe_key(urlsafe_key):
    logging.info('(db.get_from_urlsafe_key) Getting from urlsafe key: %s' % urlsafe_key)
    key = ndb.Key(urlsafe=urlsafe_key)
    logging.info('(db.get_from_urlsafe_key) Getting kind: %s and key: %s' % (key.kind(), key.id()))
    return key.get()
    
def fetch_patients():
    return Patient.query().order(Patient.last_name)

def fetch_invites():
    return Invite.query().order(-Invite.created_on)

def fetch_providers():
    return Provider.query().order(Provider.last_name)

def fetch_provider_prospects():
    all_prospects = ProviderProspect.query().order(ProviderProspect.category, ProviderProspect.last_name).fetch()

    ordered_prospects = []
        
    # order them in some logical way
    order = ['new', 'requires_followup', 'potential_champion', 'generic_person', 'unlikely']
    for o in order:
        tagged = filter(lambda p: o in p.tags, all_prospects)
        ordered_prospects.extend(tagged)
        for e in tagged:
            all_prospects.remove(e)
    
    # add anyone leftover at the end  
    ordered_prospects.extend(all_prospects)
    
    return ordered_prospects

def fetch_campaigns():
    return EmailCampaign.query().order(EmailCampaign.name)

def fetch_prospects():
    return ProviderProspect.query().order(ProviderProspect.last_name, ProviderProspect.first_name)

def fetch_bookings():
    return Booking.query().order(-Booking.created_on)

def get_bookings_for_patient(patient):
    return Booking.query(Booking.patient == patient.key).fetch()

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

def get_prospect_from_prospect_id(prospect_id):
    if prospect_id:
        return ProviderProspect.query(ProviderProspect.prospect_id == prospect_id).get()
    else:
        return None  

def get_site_logs_for_prospect(prospect):
    ''' returns all the log events for a user '''
    if prospect:
        return SiteLog.query(SiteLog.prospect == prospect.key).order(-SiteLog.access_time).fetch()
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


def get_campaign_form_name(campaign_name):
    if campaign_name:
        return EmailCampaign.query(EmailCampaign.name == campaign_name).get()
    else:
        return None
    