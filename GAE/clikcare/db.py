'''
    database access
'''
from google.appengine.ext import db as gdb
import logging
import types
from datetime import datetime
from data import Booking
from data import Patient
from data import Provider
  
def set_all_properties_on_entity_from_multidict(entity, multidict):
    ''' fancy way to set all properties on an entity from a multidict (posted form '''
    
    for prop in iter(entity.properties()):
        if multidict.has_key(prop):
            logging.info("type for property " + prop + " is " + str(type(getattr(entity, prop))))
            if isinstance(getattr(entity, prop), str):
                logging.info("saving key->value : " + prop + "->" + multidict.getone(prop))
                setattr(entity, prop, multidict.getone(prop))
            elif isinstance(getattr(entity, prop), list):
                logging.info("saving key->value:" + prop + " -> " + str(multidict.getall(prop)))
                setattr(entity, prop, multidict.getall(prop))
            elif isinstance(getattr(entity, prop), types.NoneType):
                logging.info("saving key->value for NoneType : " + prop + "->" + multidict.getone(prop))
                
                # set a boolean, not detected as boolean from Entity...
                if multidict.getone(prop) == 'True':
                    setattr(entity, prop, True)
                else:
                    setattr(entity, prop, multidict.getone(prop))
            else:
                logging.info("Got a property of unknown instance: " + str(type(getattr(entity, prop))))
        else:
            logging.info("Property not found in request: " + str(prop))
        
  
def storeBooking(r, patient=None, provider=None):
    logging.info('Saving Booking from:' + str(r))
    booking = Booking()
    booking.requestCategory = r['bookingCategory']
    booking.requestRegion = r['bookingRegion']
    requestDateString = r['bookingDate']
    requestTimeString = r['bookingTime']
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
    set_all_properties_on_entity_from_multidict(patient, r)
    
    # store
    patient_key = patient.put()
    logging.info('Saved patient key:' + str(patient_key))
    logging.info(vars(patient))
    
    # link openIDuser - is this still relevant?
    #patient.user = user
    
    return patient

def getPatientFromUser(user):
    logging.info('Fetching patient from User: %s' % user)
    query = gdb.GqlQuery("SELECT * FROM Patient WHERE user = :1", user)
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
    providersQuery = gdb.GqlQuery('''Select * from Provider WHERE category = :1 AND region = :2''', category, region)
    providerCount = providersQuery.count(limit=50)
    logging.info('Found {0} providers in category and region. Narrowing down list using schedule...'.format(providerCount))
    for p in providersQuery:
        scheduleQuery = gdb.GqlQuery('''Select * from Schedule WHERE provider = :1 AND day = :2''', p, requestDay)
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
    providers = gdb.GqlQuery("SELECT * from Provider ORDER BY last_name ASC LIMIT 50")
    return providers

def initProvider(provider_email):
    ''' inititalize provider with email. return the provider's key '''
    new_provider = Provider()
    new_provider.email = provider_email
    provider_key = new_provider.put()
    return provider_key

def getProvider(request):
    ''' get provider from a request dict, key = provider_key'''
    provider_key = request.get('provider_key')
    return Provider.get(provider_key)
    
def getOrCreateProvider(provider_key):
    if (provider_key):
        logging.info('Getting existing provider with key:' + provider_key)
        provider = Provider.get(provider_key)
    else:
        logging.info('Creating new provider')
        provider = Provider()
    return provider


def storeProvider(r):
    # r is a MultiDict object from the request
    logging.info("Storing provider profile from request:" + str(r.__dict__))
    provider = getOrCreateProvider(r['provider_key'])
    
    # set all the properties
    set_all_properties_on_entity_from_multidict(provider, r)
    
    # store
    provider_key = provider.put()
    logging.info('Saved provider key:' + str(provider_key))
    logging.info(vars(provider))
    return provider_key


def getProviderFromEmail(email):
    q = Provider.all()
    q.filter("email =", email)
    provider = q.get()
    logging.debug('Key for email %s is %s' % (email, unicode(provider.key())))
    return provider   


def get_provider_from_activation_key(activation_key):
    q = Provider.all()
    q.filter('activation_key = ', activation_key)
    provider = q.get()
    logging.debug('Found provider %s from activation_key: %s' % (provider, activation_key))
    return provider
