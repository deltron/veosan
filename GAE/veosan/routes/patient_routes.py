# Patient Routes
from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import patient, booking


patient_routes = PathPrefixRoute('/patient', [
                    Route('/bookings', patient.ListPatientBookings),
                    Route('/new', patient.NewPatientHandler),
                    Route('/book', booking.BookingHandler),
               ])
