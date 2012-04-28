'''
    database access
'''
from google.appengine.ext import db as gdb
import logging
from datetime import datetime
from data import Booking
from data import Patient
from data import Provider
  
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
    
def storePatient(r):
    patient = Patient()
    patient.firstName = r['firstName']
    patient.lastName = r['lastName']
    patient.email = r['email']
    patient.telephone = r['telephone']
    patient.put()
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
        schedules = scheduleQuery.fetch(limit=1)
        if (len(schedules) > 0):
            s = schedules[0]
            # manually check if hours match (because of BadFilterError: "Only one property per query may have inequality filters")
            if (requestStartTime >= s.startTime & requestEndTime <= s.endTime):
                logging.info('Found schedule match for provider {0}, schedule {1}:'.format(p, s))
                providers.append(p)
            else:
                logging.info('Schedule hours do not match {0}'.format(s))
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
    providers = gdb.GqlQuery("SELECT * from Provider ORDER BY lastName ASC LIMIT 50")
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

def storeProvider(request):
    provider = getOrCreateProvider(request.get('provider_key'))
    # profile
    provider.category = request.get('category', provider.category)
    provider.specialty = request.get('specialty', provider.specialty)
    provider.school = request.get('school', provider.school)
    provider.degree = request.get('degree', provider.degree)
    provider.startYear = request.get('startYear')
    # address
    provider.firstName = request.get('firstName', provider.firstName)
    provider.lastName = request.get('lastName', provider.lastName)
    provider.email = request.get('email', provider.email)
    provider.phone = request.get('phone', provider.phone)
    provider.region = request.get('region', provider.region)
    provider.address = request.get('address', provider.address)
    provider.city = request.get('city', provider.city)
    provider.postalCode = request.get('postalCode', provider.postalCode)
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
    