import logging
from handler.base import BaseHandler
# webapp2 auth service
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
from webapp2_extras.i18n import gettext as _
# google user service
from google.appengine.api import users
from webapp2_extras.appengine.users import admin_required as google_admin_required
# clik
from forms.login import LoginForm
import data
from data.model import Provider


# Roles
PROVIDER_ROLE = 'Provider'
PATIENT_ROLE = 'Patient'

# admin_required uses the google user system
admin_required = google_admin_required

def provider_required(handler_method):
    '''
        Decorator: Checks session for authenticated provider (or google admin)
    '''
    
    def check_provider_key(self):
        user = self.get_current_user()
        if user:
            provider = data.db.get_provider_profile(user)
            
            # if there is a key in the request, make sure it matches the logged in user
            if provider:
                return provider.key.urlsafe() == self.request.get('key')
            else:
                logging.info('provider_required failed. Provider key does not match request key %s <> $s' % (provider.key.urlsafe(), self.request.get('key')))
        else:
            logging.info('provider_required failed: User is None')
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
            patient = data.db.get_patient_profile(user)
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



class LoginHandler(BaseHandler):
    '''
        GET shows login page
        POST checks username, password, logs in user and redirect to start page
    '''
    def get(self):
        self.render_template('login.html', form=LoginForm())

    def post(self):
        login_form = LoginForm(self.request.POST)
        if login_form.validate():
            email = self.request.POST.get('email')
            password = self.request.POST.get('password')
            remember_me = True if self.request.POST.get('remember_me') == 'on' else False
            logging.info('Trying to login email:%s' % email)
            # Username and password check
            try:
                user = self.login_user(email, password, remember_me)
                # login was succesful, User is in the session
                booking_key = self.request.POST.get('booking_key')
                if booking_key:
                    # special redirect for login during booking flow
                    self.redirect('/patient/book?bk=%s' % booking_key)
                else:
                    # default redirects
                    profiles = data.db.get_user_profiles(user)
                    logging.info('profiles: %s' % profiles)
                    # redirect to the first profile type
                    if len(profiles) > 0:
                        profile = profiles[0]
                        if isinstance(profile, Provider):
                            redirect_url = profile.get_edit_link('/provider/bookings')
                            self.redirect(redirect_url)
                        else:
                            self.redirect('/')
                    else:
                        logging.error('User %s logged in without roles')
                        error_message = 'Your profile is not activated. Please contact us.'
                        self.render_template('login.html', form=login_form, error_message=error_message)
                
            except (InvalidAuthIdError, InvalidPasswordError), e:
                # throws InvalidAuthIdError if user is not found, throws InvalidPasswordError if provided password doesn't match with specified user
                error_message = _(u'Login failed. Try again.')
                self.render_template('login.html', form=login_form, error_message=error_message)
        else:
            # form validation error
            self.render_template('login.html', form=login_form)



class LogoutHandler(BaseHandler):
    '''
        Unset user session and redirect to index
    '''
    def get(self):
        self.auth.unset_session()
        self.redirect('/')



