'''
    database access
'''
from data import Booking
from data import Patient
            
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