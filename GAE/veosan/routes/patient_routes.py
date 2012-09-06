# Patient Routes
from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import patient


patient_routes = [
                  PathPrefixRoute('/patient', [
                                            Route('/bookings', patient.ListPatientBookings),
                                       ]),
                  ]
