import logging, urlparse
from datetime import date

# GAE
from webapp2_extras.i18n import gettext as _
from webapp2_extras import security 
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from google.appengine.api import users

# veo
from base import BaseHandler
import data.db as db
import auth
from patient import PatientBaseHandler
from forms.user import PasswordForm, LoginForm, ProviderSignupForm1
import mail
from google.appengine.ext import ndb
from handler.booking_pkg.booking_base_handler import BookingBaseHandler

class UserBaseHandler(BaseHandler):   
    ''' User management handler:
            - password set and reset
            - activation
    '''
    
        
    def render_terms(self, provider, terms_form, **kw):
        self.render_template('provider/provider_terms.html', provider=provider, terms_form=terms_form, **kw)

    def render_booking_confirmed_and_password_selection(self, user=None, password_form=None, **kw):
        if not password_form:
            password_form = PasswordForm().get_form()
            
        if not user:
            user = self.get_current_user()
            
        if user:
            # check if provider or patient          
            if auth.PROVIDER_ROLE in user.roles:
                provider = db.get_provider_from_user(user)
                if provider:
                    self.render_template('user/password.html', provider=provider, form=password_form, **kw)
                else:
                    logging.error('(UserBaseHandler.render_password_selection) no provider found for user %s ' + user.get_email())

            elif auth.PATIENT_ROLE in user.roles:
                patient = db.get_patient_from_user(user)
                if patient:
                    confirmed_bookings = PatientBaseHandler.confirm_all_unconfirmed_bookings(patient)
                    # render page
                    self.render_template('patient/email_confirmation_link_clicked.html', patient=patient, confirmed_bookings=confirmed_bookings, form=password_form, **kw)
                    # email providers
                    for booking in confirmed_bookings:
                        mail.email_booking_to_provider(self, booking)
                else:
                    logging.error('(UserBaseHandler.render_password_selection) no patient found for user %s ' + user.get_email())

            else:
                logging.error('(UserBaseHandler.render_password_selection) no user given, cannot render password selection')
        
    def render_login(self, next_action=None, key=None, **kw):
        login_form = LoginForm().get_form()
        
        if next_action == 'accept':
            if key:
                # get the source provider
                provider_network_connection = ndb.Key(urlsafe = key).get()
                
                # get the target provider (ie. the guy clicking the email)
                target_provider = provider_network_connection.target_provider.get()
                login_form = LoginForm().get_form(obj=target_provider)
                
        if next_action == 'booking':
            if key:
                # get the patient's email
                booking = ndb.Key(urlsafe = key).get()
                patient_from_booking = booking.patient.get()
                
                login_form = LoginForm().get_form(obj=patient_from_booking)

        
        self.render_template('user/login.html', login_form=login_form, next_action=next_action, key=key, **kw)


class InviteHandler(UserBaseHandler):
    def get(self, invite_token=None):
        invite = db.get_invite_from_token(invite_token)
        if invite:
            invite_provider = invite.provider.get()
            
            # update invite status
            invite.link_clicked = True
            invite.put()
            
            logging.info("(InviteHandler.get) Invite token for %s from %s " % (invite.email, invite_provider.vanity_url))
    
            provider_signup_form = ProviderSignupForm1().get_form()
            provider_signup_form['email'].data = invite.email
            provider_signup_form['first_name'].data = invite.first_name
            provider_signup_form['last_name'].data = invite.last_name
    
            self.render_template('user/signup_provider_1.html', provider_signup_form=provider_signup_form)
        else:
            self.redirect("/login")    


class PasswordHandler(UserBaseHandler):
    def get(self, signup_token=None):
        user = db.get_user_from_signup_token(signup_token)
        
        self.render_booking_confirmed_and_password_selection(user=user, signup_token=signup_token)
        
    def post(self, signup_token=None):
        password_form = PasswordForm().get_form(self.request.POST)
        
        user = db.get_user_from_signup_token(signup_token)
        
        # check for password reset token
        if user == None:
            user = db.get_user_from_resetpassword_token(signup_token)
        
        provider = db.get_provider_from_user(user)
        patient = db.get_patient_from_user(user)
        
        if user and password_form.validate():        
            # get password from request
            password = self.request.get('password')
                
            # hash password (same as passing password_raw to user_create)
            password_hash = security.generate_password_hash(password, length=12)    
            user.password = password_hash
            user.put()
            
            # login with new password
            self.login_user(user.get_email(), password)

            if user.signup_token:
                # new user
                logging.info('(PasswordHandler.post) New user just set their password: %s' % user.get_email())
                
                # delete the signup token
                self.delete_signup_token(user)
            
                if patient:
                    welcome_message = _("Welcome to Veosan! Profile confirmation successful.")
                    BookingBaseHandler.render_confirmed_patient(self, patient, success_message=welcome_message)

            elif user.resetpassword_token:
                # not a returning user, must be a password reset
               
                # clear the password reset key to prevent further shenanigans
                self.delete_resetpassword_token(user)
                
                logging.info('(PasswordHandler.post) Set new password for email %s' % user.get_email())

                self.login_user(user.get_email(), password)

                if auth.PROVIDER_ROLE in user.roles:
                    self.redirect('/provider/message/reset/' + provider.vanity_url)
                    self.log_event(user, "Password reset for user")

                
                if auth.PATIENT_ROLE in user.roles:
                    PatientBaseHandler.render_bookings(self, patient, success_message=_("Welcome back! Password has been reset.")) 

        # password form was not validate, re-render and try again!
        else:
            self.render_booking_confirmed_and_password_selection(user, password_form=password_form, signup_token=signup_token)

        


class ResetPasswordHandler(UserBaseHandler):
    def get(self, resetpassword_token=None):
        ''' Someone coming back with a password reset token '''
        #parse URL to get password reset key
        if resetpassword_token:
            user = self.validate_resetpassword_token(resetpassword_token)
            if user:            
                # got a good user for that password reset token, show the password form
                self.render_booking_confirmed_and_password_selection(user=user, signup_token=resetpassword_token)
            else:
                # no user found for password reset key, send them to the login page
                error_message = "Sorry, we can't find anyone for that password reset link. Links are expired after 24 hours, please try again."
                logging.info("(ProviderResetPasswordHandler.get) can't find anyone for that password reset link: %s" % resetpassword_token)
                self.render_login(error_message=error_message)
        else:
            logging.info('(ProviderResetPasswordHandler.get) No password reset key in request')
        
        
    def post(self):
        ''' Someone forgot their password, generate a token and send email '''
        email = self.request.get('email')

        logging.info("(ProviderResetPasswordHandler.post) got password reset request for email: %s" % email)
        if email:            
            user = db.get_user_from_email(email)
        
            if user:
                self.create_resetpassword_token(user)
                
                # resetpassword url
                url_obj = urlparse.urlparse(self.request.url)
                passwordreset_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/user/resetpassword/' + user.resetpassword_token, '', '', ''))
                logging.info('(ProviderResetPasswordHandler.post) password reset URL:' + passwordreset_url)
            
                # send email
                mail.email_user_password_reset(self.jinja2, user, passwordreset_url)
            
                # render the login page with success message
                success_message = _('Password reset instructions have been sent to your address on file.')
                logging.info("(ProviderResetPasswordHandler.post) " + success_message)
                self.render_login(success_message=success_message)
            else:
                logging.info("(ProviderResetPasswordHandler.post) Can't reset password, no provider exists for email: %s" % email)
                self.render_login()


class ActivationHandler(UserBaseHandler):
    def get(self, signup_token=None):
        if signup_token:
            user = self.validate_signup_token(signup_token)
            if user:                        
                if auth.PATIENT_ROLE in user.roles:
                    logging.info('(ActivationHandler) activating patient: %s' % user.get_email())

                    patient = db.get_patient_from_user(user)
                    
                    if patient:
                        # the patient's email is confirmed, any unconfirmed bookings are confirmed
                        
                        # make the patient choose a password
                        self.render_booking_confirmed_and_password_selection(user=user, signup_token=signup_token)
                    else:
                        # no patient found for user & token combination, send them to the login page
                        logging.info('(ActivationHandler) no patient found for user & token combination')
                        self.redirect("/login")

            else:
                # no user found for token combination, probably expired link (or just garbage).
                logging.info('(ActivationHandler) no user found for signup token %s' % signup_token)
                
                error_message = _("Activation link has expired. Please <a href='/contact'>contact us</a> to receive a new activation.")
                self.render_login(error_message=error_message)

        else:
            logging.info('(ActivationHandler) No signup token in request')
            self.redirect("/login")


class LoginHandler(UserBaseHandler):
    '''
        GET shows login page
        POST checks username, password, logs in user and redirect to start page
    '''
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
                    target_url = '/patient/bookings'
                    self.redirect(target_url)
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
            email = self.request.POST.get('email')
            password = self.request.POST.get('password')
            remember_me = True if self.request.POST.get('remember_me') == 'on' else False
            logging.info('(LoginHandler.post) Trying to login email: %s' % email)

            # Username and password check
            try:
                user = self.login_user(email, password, remember_me)
                
                # set the language from user profile
                self.set_language(user.language)

                # login was succesful, User is in the session
                if next_action == 'booking':
                    booking = ndb.Key(urlsafe=key).get()
                
                    if booking:
                        # special redirect for login during booking flow
                        
                        # is this supposed to confirm or something?
                        self.redirect('/patient/bookings')
                
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
                        self.redirect('/patient/bookings')
                        
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






