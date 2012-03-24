'''
    database access
'''
from data import Booking
from data import Patient
            
def storeBooking(request):         
    booking = Booking()
    booking.requestSpecialty = request.get('categories')
    booking.requestLocation = request.get('regions')
    booking.put()
    
    
def storePatient(request):         
    patient = Patient()
    patient.firstname = request.get('firstName')
    patient.lastname = request.get('lastName')
    patient.put()