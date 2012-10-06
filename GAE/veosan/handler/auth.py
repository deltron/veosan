import logging
# google user service
from google.appengine.api import users
from webapp2_extras.appengine.users import admin_required as google_admin_required
# veo
import data


# Roles
PROVIDER_ROLE = 'provider'
PATIENT_ROLE = 'patient'
ADMIN_ROLE = 'admin'

# admin_required uses the google user system
admin_required = google_admin_required

def provider_required(handler_method):
    '''
        Decorator: Checks session for authenticated provider (or google admin)
    '''
    
    def check_provider_key(self, vanity_url = None):
        user = self.get_current_user()
        if user:
            provider = data.db.get_provider_from_user(user)
            
            # if there is a key in the request, make sure it matches the logged in user
            if vanity_url:
                return provider.vanity_url == vanity_url
            elif self.request.get('key'):                
                return provider.key.urlsafe() == self.request.get('key')
            else:
                logging.info('(decorator @provider_required.check_provider_key) provider_required failed. Provider key does not match request key %s != %s' % (provider.key.urlsafe(), self.request.get('key')))
        else:
            logging.info('(decorator @provider_required.check_provider_key) provider_required failed: User is None')
        return False

    def check_provider_login(self, vanity_url = None, *args, **kwargs):
        # admin
        if users.is_current_user_admin():
            handler_method(self, vanity_url, *args, **kwargs)
            
        # provider logged in with key matching request key
        elif check_provider_key(self, vanity_url):
            handler_method(self, vanity_url, *args, **kwargs)
            
        else:
            # has a vanity url but not logged in, redirect to provider's public profile
            if vanity_url:
                self.redirect('/' + vanity_url)
            else:
                self.redirect('/login')
                
    # decorator returns check_login function    
    return check_provider_login


def patient_required(handler_method):
    '''
        Decorator: Checks session for authenticated patient (or google admin)
    '''
    
    def check_patient_key(self, patient_key = None):
        user = self.get_current_user()
        if user:
            patient = data.db.get_patient_from_user(user)
            if patient:
                if patient_key:
                    return patient.key.urlsafe() == patient_key
                else:
                    logging.error('patient_required failed. patient from user and patient from key do not match')  
            else:
                logging.info('patient_required failed. User does not have a patient profile')
        else:
            logging.info('provider_required failed: User is None')
        return False

    def check_patient_login(self, patient_key = None, *args, **kwargs):
        # admin
        if users.is_current_user_admin():
            handler_method(self, patient_key, *args, **kwargs)
        # patient logged in with key matching booking.patient or ...
        elif check_patient_key(self):
            handler_method(self, patient_key, *args, **kwargs)
        else:
            self.redirect('/login', abort=True)
            
    # decorator returns check_login function    
    return check_patient_login




