'''
    database access
'''
#from google.appengine.ext import db as gdb
from google.appengine.ext import ndb
import logging
from datetime import datetime
from data.model import Booking, Patient, User, PartialProvider, LogEvent
from data.model_pkg.network_model import Invite, ProviderNetworkConnection
from data.model_pkg.provider_model import Provider, ProviderAccount
import utilities
from data.model_pkg.prospect_model import Campaign, ProviderProspect, ProspectNote
from data.model_pkg.site_model import SiteCounter, SiteConfig, SiteLog,\
    DomainSetup
from google.appengine.ext.ndb.query import Cursor
  
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

def fetch_page_of_provider_prospects(cursor_key=None, page_size=50, search_keyword=None):
    ''' 
        Returns three values: prospects, next_curs, prev_curs
        
        Search uses a workaround to imitate LIKE:
        http://stackoverflow.com/questions/47786/google-app-engine-is-it-possible-to-do-a-gql-like-query
    
    '''
    cursor = Cursor(urlsafe=cursor_key)
    if search_keyword:
        limit = search_keyword + u"\ufffd"
        query = ProviderProspect.query(ProviderProspect.last_name >= search_keyword, ProviderProspect.last_name < limit)
        
        query = query.order(ProviderProspect.last_name)
    else:
        query = ProviderProspect.query()
    # forward and back
    forward_query = query.order(ProviderProspect.category, ProviderProspect.last_name, ProviderProspect.key)
    backward_query = query.order(-ProviderProspect.category, -ProviderProspect.last_name, -ProviderProspect.key)
    # fetch next
    prospects, next_curs, more = forward_query.fetch_page(page_size, start_cursor=cursor)
    logging.info('next_curs: %s  more: %s' % (next_curs, more))
    # fetch prev (just to get cursor position)
    if cursor_key:
        reversed_cursor = cursor.reversed()
        prev_prospects, prev_curs, prev_more = backward_query.fetch_page(page_size, start_cursor=reversed_cursor)
        # reverse the cursor (GAE docs is wrong on this)
        if prev_curs:
            prev_curs = prev_curs.reversed()
    else:
        prev_curs = None
        prev_more = None
    
    if not more:
        next_curs = None

    #if not prev_more:
    #    prev_curs = None
    return prospects, next_curs, prev_curs

#    ordered_prospects = []
#    # order them in some logical way
#    order = ['new', 'requires_followup', 'potential_champion', 'generic_person', 'unlikely']
#    for o in order:
#        tagged = filter(lambda p: o in p.tags, all_prospects)
#        ordered_prospects.extend(tagged)
#        for e in tagged:
#            all_prospects.remove(e)
#    
#    # add anyone leftover at the end  
#    ordered_prospects.extend(all_prospects)
#    return ordered_prospects

def fetch_campaigns():
    return Campaign.query().order(-Campaign.created_on)

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

def get_provider_prospect_from_email(email):
    prospect = ProviderProspect.query(ProviderProspect.email == email).get()
    logging.debug('ProviderProspect for email %s is %s' % (email, prospect))
    return prospect

def get_partial_provider_from_email(email):
    return PartialProvider.query(PartialProvider.email == email).get()

def get_patient_from_email(email):
    return Patient.query(Patient.email == email).get()

def get_all_vanity_urls():
    return Provider.query().fetch(projection=['vanity_url'])

def get_user_from_email(email):
    return User.query(User.auth_ids == email).get()

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
        
def get_provider_network_connection(source_key, target_key):
    return ProviderNetworkConnection.query(ProviderNetworkConnection.source_provider == source_key, ProviderNetworkConnection.target_provider == target_key).get()
    
def get_schedule_for_date_time(provider, book_date_string, book_time_string):
    book_weekday_index = datetime.strptime(book_date_string, '%Y-%m-%d').weekday()
    (book_weekday_key, book_weekday_label) = utilities.time.get_day_of_the_week_from_python_weekday(book_weekday_index)
    
    book_time = datetime.strptime(book_time_string, '%H:%M')
    book_time_int = int(book_time.hour)
    
    schedules = provider.get_schedules()
    for schedule in schedules:
        if book_weekday_key == schedule.day:
            if book_time_int >= schedule.start_time and book_time_int <= schedule.end_time:
                return schedule


def get_campaign_form_name(campaign_name):
    if campaign_name:
        return Campaign.query(Campaign.name == campaign_name).get()
    else:
        return None


#def get_prospect_campaigns(prospect):
#    return Campaign.query(Campaign.prospects == prospect.key).order(-Campaign.created_on).fetch()
#
#def get_campaign_email_notes_count(campaign):
#    return ProspectNote.query(ProspectNote.campaign == campaign.key, ProspectNote.note_type == 'email').count()
#    

def get_signup_from_origin(origin):
    if origin:
        return Provider.query(Provider.signup_origin == origin).count()

def get_paid_from_origin(origin):
    if origin:
        provider_keys = Provider.query(Provider.signup_origin == origin).fetch(keys_only=True)
        if provider_keys:
            provider_account_count = ProviderAccount.query(ProviderAccount.provider.IN(provider_keys)).count()
            return provider_account_count
        else:
            return 0


def get_domain_setup(domain):
    if domain:
        return DomainSetup.query(DomainSetup.domain_name == domain).get()

def get_all_domain_setup():
    return DomainSetup.query().fetch()

