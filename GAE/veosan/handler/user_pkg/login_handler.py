
import mail
from data import db
from google.appengine.ext import ndb
from google.appengine.api import users
import datetime
import logging
from forms.user import LoginForm
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from handler import auth
from handler.user_pkg.user_base_handler import UserBaseHandler
from webapp2_extras.i18n import lazy_gettext as _



class LoginHandler(UserBaseHandler):
    
    def get_en(self, next_action=None, key=None):
        self.set_language('en')
        self.get(next_action, key)
        
    def get_fr(self, next_action=None, key=None):
        self.set_language('fr')
        self.get(next_action, key)
    
    '''
        GET shows login page
        POST checks username, password, logs in user and redirect to start page
    '''

    def email_and_confirm_booking(self, booking):
        # email patient
        if not booking.email_sent_to_patient:
            mail.email_booking_to_patient(self, booking)
        
        # email provider
        if not booking.email_sent_to_provider:
            mail.email_booking_to_provider(self, booking)
            
        booking.confirmed = True
        booking.put()
        
        patient_user = booking.patient.get().user.get()
        patient_user.confirmed = True
        patient_user.put()
        
        

    def get(self, next_action=None, key=None):
        ''' Show login page '''
        
        user = self.get_current_user()
        if user and next_action and key:
            # if already logged in
            provider_from_user = db.get_provider_from_user(user)
            patient_from_user = db.get_patient_from_user(user)
            
            # check if logged in provider is the provider from
            # already logged in, don't login again
            if next_action == 'accept':
                provider_network_connection = ndb.Key(urlsafe=key).get()
                target_provider_key = provider_network_connection.target_provider

                if provider_from_user.key == target_provider_key:
                    # the target provider is logged in, accept the connection bypassing login
                    target_url = '/provider/network/' + provider_from_user.vanity_url + '/accept/' + key
                    self.redirect(target_url)
                else:
                    self.render_login(next_action=next_action, key=key)
            
            elif next_action == 'booking':
                booking = ndb.Key(urlsafe=key).get()
                
                if patient_from_user.key == booking.patient:
                    self.email_and_confirm_booking(booking)

                    self.redirect('/patient/bookings/' + patient_from_user.key.urlsafe())
                else:
                    self.render_login(next_action=next_action, key=key)
                
        else:
            # check if an admin is logged in, if so don't proceed
            google_user = users.get_current_user()
            if google_user and users.is_current_user_admin():
                self.render_login(error_message='Logged in as admin already.')
            else:
                # no admin, not next_action, show the plain ol' login screen
                self.render_login(next_action=next_action, key=key)
        

    def post(self, next_action=None, key=None):
        ''' checks username, password, logs in user and redirect to start page '''
        
        login_form = LoginForm().get_form(self.request.POST)
        if login_form.validate():
            email = login_form['email'].data
            password = login_form['password'].data
            remember_me = login_form['remember_me'].data
            
            logging.info('(LoginHandler.post) Trying to login email: %s' % email)

            # Username and password check
            try:
                user = self.login_user(email, password, remember_me)
                user.last_login = datetime.datetime.now()
                user.put()
                
                # set the language from user profile
                self.set_language(user.language)

                # login was succesful, User is in the session
                if next_action == 'booking':
                    # moved booking up here since it can come from any role (provider or patient)
                    booking = ndb.Key(urlsafe=key).get()
                    patient_from_user = db.get_patient_from_user(user)

                    if patient_from_user.key == booking.patient:
                        self.email_and_confirm_booking(booking)
                        self.redirect('/patient/bookings/' + patient_from_user.key.urlsafe())
                
                else:
                    # check role of user, redirect to appropriate page after login
                    if auth.PROVIDER_ROLE in user.roles:
                        provider = db.get_provider_from_user(user)
                        logging.info('(LoginHandler.post) User %s logged in as provider, redirecting to profile page', user.get_email())

                        # check the action, if it's from a connection do that first
                        # and then redirect back to profile page with a message
                        if next_action == 'connect':
                            connected_provider_key = ndb.Key(urlsafe=key)
                            connected_provider = connected_provider_key.get()
                            target_url = '/' + connected_provider.vanity_url + '/connect'
                            self.redirect(target_url)

                        elif next_action == 'accept':
                            target_url = '/provider/network/' + provider.vanity_url + '/accept/' + key
                            self.redirect(target_url)

                        elif provider.display_welcome_page:     
                            self.redirect('/provider/welcome/' + provider.vanity_url)
                        else:
                            self.redirect('/provider/profile/%s' % provider.vanity_url)

                        # log the event
                        self.log_event(user, "Provider Logged In")

                    elif auth.PATIENT_ROLE in user.roles:
                        patient = db.get_patient_from_user(user)
                        
                        logging.info('(LoginHandler.post) User %s logged in as patient, redirecting to / page', user.get_email())
                        self.redirect('/patient/bookings/' + patient.key.urlsafe())
                        
                    else:
                        logging.error('(LoginHandler.post) User %s logged in without roles', user.get_email())
                        error_message = 'Your account is not activated. Please check your email for an activation message or <a href="/contact">contact us</a> if you require assistance.'
                        self.render_template('user/login.html', login_form=login_form, error_message=error_message)
                
            except (InvalidAuthIdError, InvalidPasswordError), e:
                # throws InvalidAuthIdError if user is not found, throws InvalidPasswordError if provided password doesn't match with specified user
                error_message = _(u'Login failed. Try again.')
                self.render_template('user/login.html', login_form=login_form, error_message=error_message)
            except AttributeError, ae:
                logging.warn('User has not password, authentication fails %s' % ae)
                #error_message = _(u'Your account is not yet activated')
                #self.render_template('user/resend.html', error_message=error_message)
                
        else:
            # form validation error
            self.render_template('user/login.html', login_form=login_form)



class LogoutHandler(UserBaseHandler):
    '''
        Unset user session and redirect to index
    '''
    def get(self):
        user = self.get_current_user()
        if user:
            logging.debug("(LogoutHandler.get) Logging out user: %s" % user.get_email())
            
            # log the event
            self.log_event(user, "Logged out")

        self.auth.unset_session()
        self.redirect('/')

