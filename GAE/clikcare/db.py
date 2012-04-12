'''
    database access
'''
from google.appengine.ext import db as gdb
import logging
from data import Booking
from data import Patient
from data import Provider
  
def storeBooking(r, patient, provider):
    booking = Booking()
    booking.requestSpecialty = r['bookingCategory']
    booking.requestLocation = r['bookingRegion']
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

   
def fetchProviders():
    providers = gdb.GqlQuery("SELECT * from Provider ORDER BY lastName ASC LIMIT 50")
    return providers

def initProvider(provider_email):
    ''' inititalize provider with email. return the provider's key '''
    new_provider = Provider()
    new_provider.email = provider_email
    provider_key = new_provider.put()
    return provider_key

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
    provider.specialty = request.get('lastName', provider.specialty)
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
    