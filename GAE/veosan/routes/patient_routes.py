# Patient Routes
from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import patient
from handler.patient_pkg import address_handler

def get_routes():
    return [
                PathPrefixRoute('/patient', [
                                            Route('/bookings/<patient_key>', patient.ListPatientBookings),
                                            Route('/address/<patient_key>', address_handler.PatientEditAddressHandler),

                                       ]),
            ]
