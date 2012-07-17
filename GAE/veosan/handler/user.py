import logging, random, sha, urlparse
from datetime import date
# veo
from base import BaseHandler
import data.db as db
import auth
from data import model
from patient import PatientBaseHandler
from provider import ProviderBaseHandler
from booking import BookingBaseHandler
from forms.user import ProviderTermsForm, PasswordForm, LoginForm
import mail
from webapp2_extras.i18n import gettext as _
from webapp2_extras import security 
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError


class UserBaseHandler(BaseHandler):   
    ''' User management handler:
            - password set and reset
            - activation
    '''
    
        
    def render_terms(self, provider, terms_form, **kw):
        self.render_template('provider/provider_terms.html', provider=provider, terms_form=terms_form, **kw)

    def render_password_selection(self, user=None, password_form=None, **kw):
        if not password_form:
            password_form = PasswordForm()
            
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
                    self.render_template('user/password.html', patient=patient, form=password_form, **kw)
                else:
                    logging.error('(UserBaseHandler.render_password_selection) no patient found for user %s ' + user.get_email())

            else:
                logging.error('(UserBaseHandler.render_password_selection) no user given, cannot render password selection')
        
    def render_login(self, **kw):
        self.render_template('user/login.html', form=LoginForm().get_form(), **kw)


class ProviderTermsHandler(UserBaseHandler):
    def get(self, vanity_url = None):
        # get provider from vanity url
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        # if no provider, try to get one by checking the logged in user
        if provider == None:
            user = self.get_current_user()
            # make sure user is a provider
            if user and auth.PROVIDER_ROLE in user.roles:
                provider = db.get_provider_from_user(user)
            else:
                logging.error("(ProviderTermsHandler.get) Requested terms but can't get the provider from a key or user")   
        
        terms_form = ProviderTermsForm().get_form(obj=provider)
        self.render_terms(provider, terms_form=terms_form)
    
    def post(self, vanity_url = None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        terms_form = ProviderTermsForm().get_form(self.request.POST)
        if terms_form.validate():
            # Save signature and terms agreement
            provider.terms_agreement = self.request.get('terms_agreement') == u'True'
            provider.terms_date = date.today()
            
            # set status to enabled
            provider.status = 'client_enabled'
            
            provider.put()
            
            user = provider.user.get()
            
            # Go to the password selection page
            self.redirect('/user/password/' + user.signup_token)
        else:
            # did not click "I accept"
            self.render_terms(provider, terms_form=terms_form)



class PasswordHandler(UserBaseHandler):
    def get(self, signup_token = None):
        user = db.get_user_from_signup_token(signup_token)
        
        self.render_password_selection(user=user, signup_token=signup_token)
        
    def post(self, signup_token = None):
        password_form = PasswordForm(self.request.POST)
        
        user = db.get_user_from_signup_token(signup_token)
        
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
            
                provider = db.get_provider_from_user(user)
                patient = db.get_patient_from_user(user)
            
                if provider:
                    # send welcome email
                    mail.emailProviderWelcomeMessage(self.jinja2, provider)
                        
                    # Provider is Activated
                    # login automatically
                    
                    # show welcome page
                    self.redirect('/provider/new/' + provider.vanity_url)
                                   
                elif patient:
                    welcome_message = _("Welcome to Veosan! Profile confirmation successful.")
                    BookingBaseHandler.render_confirmed_patient(self, patient, success_message=welcome_message)

            elif user.resetpassword_token:
                # not a returning user, must be a password reset
               
                # clear the password reset key to prevent further shenanigans
                self.delete_resetpassword_token(user)
                
                logging.info('(PasswordHandler.post) Set new password for email %s' % user.get_email())

                self.login_user(user.get_email(), password)

                success_message = _("Welcome back! Password has been reset for %s" % user.get_email())
                
                if auth.PROVIDER_ROLE in user.roles:
                    ProviderBaseHandler.render_bookings(self, provider, success_message=success_message) 
                
                if auth.PATIENT_ROLE in user.roles:
                    PatientBaseHandler.render_bookings(self, patient, success_message=success_message) 

        # password form was not validate, re-render and try again!
        else:
            self.render_password_selection(user, password_form=password_form, signup_token=signup_token)

        


class ResetPasswordHandler(UserBaseHandler):
    def get(self, resetpassword_token=None):
        ''' Someone coming back with a password reset token '''
        #parse URL to get password reset key
        if resetpassword_token:
            user = self.validate_resetpassword_token(resetpassword_token)
            if user:            
                # got a good user for that password reset token, show the password form
                self.render_password_selection(user=user)
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
                success_message = 'Password reset instructions sent to %s' % user.get_email()
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
            
                if auth.PROVIDER_ROLE in user.roles:
                    logging.info('(ActivationHandler) activating provider: %s' % user.get_email())

                    provider = db.get_provider_from_user(user)
                
                    if provider:
                        # mark terms as not agreed
                        provider.terms_agreement = False
                        provider.terms_date = None

                        # show terms page
                        terms_form = ProviderTermsForm().get_form(obj=provider)
                        self.render_terms(provider, terms_form=terms_form, signup_token=signup_token)
                        
                    else:
                        # no provider found for user & token combination, send them to the login page
                        logging.info('(ActivationHandler) no provider found for user & token combination')
                        self.redirect("/login")
                        
                elif auth.PATIENT_ROLE in user.roles:
                    logging.info('(ActivationHandler) activating patient: %s' % user.get_email())

                    patient = db.get_patient_from_user(user)
                    
                    if patient:
                        # make the patient choose a password
                        self.render_password_selection(user=user)
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

          
class ProviderSignupHandler(UserBaseHandler):
    def post(self):
        provider_email = self.request.get('provider_email')
        provider_postalcode = self.request.get('provider_postalcode')

        message = "Received sign-up request from email->%s postal_code->%s" % (provider_email, provider_postalcode)

        logging.info(message)

        from_email = "support@veosan.com"
        subject = "Request for signup from provider"

        mail.email_contact_form(self.jinja2, from_email, subject, message)

        success_message = 'Thanks for your interest. We will be in touch soon!'
        self.render_login(success_message=success_message)
        
        

class LoginHandler(UserBaseHandler):
    '''
        GET shows login page
        POST checks username, password, logs in user and redirect to start page
    '''
    def get(self):
        ''' Show login page '''
        self.render_login()
        

    def post(self):
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
                
                # login was succesful, User is in the session
                booking_key = self.request.POST.get('booking_key')
                
                if booking_key:
                    # special redirect for login during booking flow
                    self.redirect('/patient/book?bk=%s' % booking_key)
                
                else:
                    # check role of user, redirect to appropriate page after login
                    if auth.PROVIDER_ROLE in user.roles:
                        provider = db.get_provider_from_user(user)
                        logging.info('(LoginHandler.post) User %s logged in as provider, redirecting to profile page', user.get_email())

                        self.redirect('/provider/profile/%s' % provider.vanity_url)

                    elif auth.PATIENT_ROLE in user.roles:
                        patient = db.get_patient_from_user(user)
                        
                        logging.info('(LoginHandler.post) User %s logged in as patient, redirecting to / page', user.get_email())
                        self.redirect('/patient/bookings')
                        
                    else:
                        logging.error('(LoginHandler.post) User %s logged in without roles', user.get_email())
                        error_message = 'Your account is not activated. Please check your email for an activation message or <a href="/contact">contact us</a> if you require assistance.'
                        self.render_template('user/login.html', form=login_form, error_message=error_message)
                
            except (InvalidAuthIdError, InvalidPasswordError), e:
                # throws InvalidAuthIdError if user is not found, throws InvalidPasswordError if provided password doesn't match with specified user
                error_message = _(u'Login failed. Try again.')
                self.render_template('user/login.html', form=login_form, error_message=error_message)
        else:
            # form validation error
            self.render_template('user/login.html', form=login_form)



class LogoutHandler(UserBaseHandler):
    '''
        Unset user session and redirect to index
    '''
    def get(self):
        user = self.get_current_user()
        if user:
            logging.info("(LogoutHandler.get) Logging out user: %s" % user.get_email())

        self.auth.unset_session()
        self.redirect('/')

