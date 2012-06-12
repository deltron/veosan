import logging
# google user service
from google.appengine.api import users
from webapp2_extras.appengine.users import admin_required as google_admin_required
# clik
import data


# Roles
PROVIDER_ROLE = 'provider'
PATIENT_ROLE = 'patient'

# admin_required uses the google user system
admin_required = google_admin_required

def provider_required(handler_method):
    '''
        Decorator: Checks session for authenticated provider (or google admin)
    '''
    
    def check_provider_key(self):
        user = self.get_current_user()
        if user:
            provider = data.db.get_provider_from_user(user)
            
            # if there is a key in the request, make sure it matches the logged in user
            if provider:
                return provider.key.urlsafe() == self.request.get('key')
            else:
                logging.info('(decorator @provider_required.check_provider_key) provider_required failed. Provider key does not match request key %s != %s' % (provider.key.urlsafe(), self.request.get('key')))
        else:
            logging.info('(decorator @provider_required.check_provider_key) provider_required failed: User is None')
        return False

    def check_provider_login(self, *args, **kwargs):
        # admin
        if users.is_current_user_admin():
            handler_method(self, *args, **kwargs)
        # provider logged in with key matching request key
        elif check_provider_key(self):
            handler_method(self, *args, **kwargs)
        else:
            self.redirect('/login', abort=True)
            
    # decorator returns check_login function    
    return check_provider_login


def patient_required(handler_method):
    '''
        Decorator: Checks session for authenticated patient (or google admin)
    '''
    
    def check_patient_key(self):
        user = self.get_current_user()
        if user:
            patient = data.db.get_patient_from_user(user)
            if patient:
                booking_key = self.request.get('bk')
                if booking_key:
                    booking = data.db.get_from_urlsafe_key(booking_key)
                    # match logged in patient to booking.patient
                    return patient.key.urlsafe() == booking.patient.urlsafe()
                else:
                    logging.error('patient_required failed. Booking.patient %s and logged in patient %s do not match' % (booking.patient, patient.key))  
            else:
                logging.info('patient_required failed. User does not have a patient profile')
        else:
            logging.info('provider_required failed: User is None')
        return False

    def check_patient_login(self, *args, **kwargs):
        # admin
        if users.is_current_user_admin():
            handler_method(self, *args, **kwargs)
        # patient logged in with key matching booking.patient or ...
        elif check_patient_key(self):
            handler_method(self, *args, **kwargs)
        else:
            self.redirect('/login', abort=True)
            
    # decorator returns check_login function    
    return check_patient_login




