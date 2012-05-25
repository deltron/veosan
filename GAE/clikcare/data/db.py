'''
    database access
'''
#from google.appengine.ext import db as gdb
from google.appengine.ext import ndb
import logging
import types
from datetime import datetime, date, time
from data.model import Booking, Patient, Provider
import util
  
def get_from_urlsafe_key(urlsafe_key):
    logging.info('Getting from urlsafe key: %s' % urlsafe_key)
    key = ndb.Key(urlsafe=urlsafe_key)
    logging.info('Getting kind: %s and key: %s' % (key.kind(), key.id()))
    return key.get()

def storeBooking(r, patient=None, provider=None):
    logging.info('Saving Booking from:' + str(r))
    booking = Booking()
    booking.requestCategory = r['category']
    booking.requestRegion = r['location']
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
    util.set_all_properties_on_entity_from_multidict(patient, r)
    
    # store
    patient_key = patient.put()
    logging.info('Saved patient key:' + str(patient_key))
    logging.info(vars(patient))
    
    # link openIDuser - is this still relevant?
    #patient.user = user
    
    return patient

def getPatientFromUser(user):
    logging.info('Fetching patient from User: %s' % user)
    query = Patient.query(Patient.user == user)
    #query = gdb.GqlQuery("SELECT * FROM Patient WHERE user = :1", user)
    logging.info("count:" + str(query.count()))
    patient = query.get()
    return patient

def findBestProviderForBooking(booking):
    'Returns provider that best matches: category, location, dateTime'
    category = booking.requestCategory
    region = booking.requestRegion
    date_time = booking.requestDateTime
    logging.info("request date_time x:" + str(date_time))
    requestDay = date_time.weekday()
    requestStartTime = date_time.hour
    requestEndTime = requestStartTime + 1
    logging.info('Looking for {0} in {1} available on day:{2} from {3} to {4}'.format(category, region, requestDay, requestStartTime, requestEndTime))
    providers = []
    providersQuery = Provider.query(Provider.category==category, Provider.location==region)
    #gdb.GqlQuery('''Select * from Provider WHERE category = :1 AND region = :2''', category, region)
    providerCount = providersQuery.count(limit=50)
    logging.info('Found {0} providers in category and region. Narrowing down list using schedule...'.format(providerCount))
    for p in providersQuery:
        scheduleQuery = ndb.gql('''Select * from Schedule WHERE provider = :1 AND day = :2''', p.key, requestDay)
        schedulesCount = scheduleQuery.count(limit=48)
        if (schedulesCount > 0):
            for s in scheduleQuery:
                # manually check if hours match (because of BadFilterError: "Only one property per query may have inequality filters")
                if (requestStartTime >= s.startTime & requestEndTime <= s.endTime):
                    logging.info('Found schedule match for provider {0}, schedule {1}:'.format(p, s.repr()))
                    providers.append(p)
                else:
                    logging.info('Schedule hours do not match {0}'.format(s.repr()))
        else:
            logging.info('No schedule match for provider {0} on day'.format(p, requestDay))
    logging.info('providers:' + str(providers))
    #providers = providersQuery.fetch(limit=1)
    if (len(providers) > 0):
        # TODO use ordering clause or Round-robin to find the top provider when list is longer than 1, currently uses the first in the list
        bestProvider = providers[0]
        logging.info('Found Best Provider: ' + bestProvider.fullName())
        return bestProvider
    else:
        logging.info('No Provider Found')
        return None
   
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
    util.set_all_properties_on_entity_from_multidict(provider, r)
    
    # store
    provider_key = provider.put()
    logging.info('Saved provider key:' + str(provider_key))
    logging.info(vars(provider))
    return provider_key


def getProviderFromEmail(email):
    provider = Provider.query(Provider.email == email).get()
    logging.debug('Provider for email %s is %s' % (email, provider))
    return provider   


def get_provider_from_activation_key(activation_key):
    provider = Provider.query(Provider.activation_key == activation_key).get()
    logging.debug('Found provider %s from activation_key: %s' % (provider, activation_key))
    return provider

def get_user_roles(user):
    '''
        return roles from user based on link to provider or patient
    '''
    return []