'''
    database access
'''
import logging
from data import Booking
from data import Patient
from data import Provider
            
def storeBooking(request):         
    booking = Booking()
    booking.requestSpecialty = request.get('categories')
    booking.requestLocation = request.get('regions')
    booking_key = booking.put()
    return booking_key
    
def storePatient(request):
    # create new patient
    new_patient = Patient()
    new_patient.firstName = request.get('firstName')
    new_patient.lastName = request.get('lastName')
    new_patient.email = request.get('email')
    new_patient.phone = request.get('telephone')
    patient_key = new_patient.put()
    # link to booking
    booking_key = request.get('booking')
    if (booking_key != None):
        booking = Booking.get(booking_key)
        booking.patient = new_patient
        booking.telephoneConfirmation = request.get('telephoneConfirmation') != ''
        booking.comments = request.get('comments')
        booking.put()
    return patient_key

def getOrCreateProvider(provider_key):
    if (provider_key):
        logging.info('Getting existing provider with key:' + provider_key)
        provider = Provider.get(provider_key)
    else:
        logging.info('Creating new provider')
        provider = Provider()
    return provider

def storeProvider(request):
    provider = getOrCreateProvider(request.get('provider'))
    provider.firstName = request.get('firstName')
    provider.lastName = request.get('lastName')
    provider.email = request.get('email')
    provider.phone = request.get('telephone')
    provider.region = request.get('region')
    provider.address = request.get('address')
    provider.city = request.get('city')
    provider.postalcode = request.get('postalcode')
    provider_key = provider.put()
    logging.info('Saved provider key:' + str(provider_key))
    
    