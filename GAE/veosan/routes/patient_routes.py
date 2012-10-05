# Patient Routes
from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import patient

def get_routes():
    return [
                PathPrefixRoute('/patient', [
                                            Route('/bookings', patient.ListPatientBookings),
                                            Route('/address', patient.AddressHandler),

                                       ]),
            ]
