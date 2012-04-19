'''
    database access
'''
from google.appengine.ext import db as gdb
import logging
from datetime import datetime
from data import Booking
from data import Patient
from data import Provider
  
def storeBooking(r, patient, provider):
    logging.info('Saving Booking from:' + str(r))
    booking = Booking()
    booking.requestCategory = r['bookingCategory']
    booking.requestRegion = r['bookingRegion']
    requestDateString = r['bookingDate']
    requestTimeString = r['bookingTime']
    requestDateTime = datetime.strptime(requestDateString + " " + requestTimeString, '%Y-%m-%d %H')
    booking.requestDateTime = requestDateTime
    booking.comments = r['comments']
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
    providersQuery = gdb.GqlQuery('''Select * from Provider WHERE category = :1 AND region = :2''', category, region)
    providerCount = providersQuery.count(limit=10)
    logging.info('Found {0} good provider matches. Narrowing down list...'.format(providerCount))
    providers = providersQuery.fetch(limit=1)
    if (len(providers) > 0):
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
    