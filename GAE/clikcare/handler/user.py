import logging, random, sha, urlparse
from datetime import date
#clik
from base import BaseHandler
import data.db as db
import auth
from provider import ProviderBaseHandler
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
    
        
    def render_terms(self, provider, terms_form, **extra):
        self.render_template('provider/provider_terms.html', provider=provider, form=terms_form, **extra)

    def render_password_selection(self, provider, password_form=None, **extra):
        if not password_form:
            password_form = PasswordForm()
        self.render_template('provider/password.html', provider=provider, form=password_form, **extra)
        

class ProviderTermsHandler(UserBaseHandler):
    def get(self):
        # get the provider key
        key = self.request.get('key')
        if key:
            provider = db.get_from_urlsafe_key(key)
        
        # if no key, try to find out who the provider is by checking the logged in user
        else:
            user = self.get_current_user()
            # make sure user is a provider
            if auth.PROVIDER_ROLE in user.roles:
                provider = db.get_provider_from_user(user)
        
        terms_form = ProviderTermsForm(obj=provider)
        self.render_terms(provider, terms_form=terms_form)
    
    def post(self):
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        terms_form = ProviderTermsForm(self.request.POST)
        if terms_form.validate():
            # Save signature and terms agreement
            provider.terms_agreement = self.request.get('terms_agreement') == u'True'
            provider.terms_date = date.today()
            provider.put()
            # Go to the password selection page
            self.render_password_selection(provider)
        else:
            self.render_terms(provider, terms_form=terms_form)

class ProviderResetPasswordHandler(UserBaseHandler):
    def get(self, resetpassword_key=None):
        ''' Someone coming back with a password reset token '''
        #parse URL to get password reset key
        if (resetpassword_key):
            provider = db.get_provider_from_resetpassword_key(resetpassword_key)
            
            if provider:
                # got a provider for that password reset token, show the password form
                self.render_password_selection(provider)
            else:
                # no provider found for password reset key, send them to the login page
                error_message = "Sorry we can't find anyone for that password reset link."
                logging.info("(ProviderResetPasswordHandler.get) can't find anyone for that password reset link: %s" % resetpassword_key)
                self.render_template("/login.html", form=LoginForm(), error_message=error_message)
        else:
            logging.info('(ProviderResetPasswordHandler.get) No password reset key in request')
        
        
    def post(self):
        ''' Someone forgot their password, generate a token and send email '''
        email = self.request.get('provider_email')

        logging.info("(ProviderResetPasswordHandler.post) got password reset request for email: %s" % email)
        if email:
            provider = db.get_provider_from_email(email)
        
            # Check provider has at least a first name, last name and email before activation
            if provider.email and provider.first_name and provider.last_name:
                salt = sha.new(str(random.random())).hexdigest()[:5]

                provider.resetpassword_key = sha.new(salt + provider.email + provider.first_name + provider.last_name).hexdigest()
                provider.put()
                
                # activation url
                url_obj = urlparse.urlparse(self.request.url)
                passwordreset_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/provider/resetpassword/' + provider.resetpassword_key, '', '', ''))
                logging.info('(ProviderResetPasswordHandler.post) password reset URL:' + passwordreset_url)
            
                # send email
                mail.emailProviderPasswordReset(self.jinja2, provider, passwordreset_url)
            
                # render the login page with success message
                success_message = 'Password reset instructions sent to %s' % provider.email
                logging.info("(ProviderResetPasswordHandler.post) " + success_message)
                self.render_template('login.html', form=LoginForm(), success_message=success_message)
            else:
                logging.info("(ProviderResetPasswordHandler.post) Can't reset password, no provider exists for email: %s" % email)
                self.render_template('login.html', form=LoginForm())


class PasswordHandler(UserBaseHandler):
    def get(self):
        logging.info('(PasswordHandler.get) GET not implemented on /password')
        self.redirect("/")
            
    def post(self):
        '''
            Create user and link it to the Provider
        '''

        password_form = PasswordForm(self.request.POST)

        # get provider from request
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        
        if password_form.validate():
            # get password from request
            password = self.request.get('password')
            
            # get user from provider
            user = db.get_user_from_email(provider.email)
            
            # set password (same as passing password_raw to user_create)
            password_hash = security.generate_password_hash(password, length=12)    
            user.password = password_hash
            user.put()
         
             
            if auth.PROVIDER_ROLE in user.roles:
                
                # this was a password reset
                if provider.resetpassword_key:
                    # clear the password reset key from provider to prevent further shenanigans
                    provider.resetpassword_key = None
                    provider.put()
                
                    logging.info('(PasswordHandler.post) Set new password for email %s' % provider.email)

                    self.login_user(provider.email, password)

                    success_message = _("Welcome back! Password has been reset for %s" % provider.email)
                    ProviderBaseHandler.render_bookings(self, provider, success_message=success_message)

                else:
                    logging.info('(PasswordHandler.post) New user just set their password: %s' % provider.email)
                    
                    # delete the signup token
                    self.delete_signup_token(user)
                    
                    # send welcome email
                    mail.emailProviderWelcomeMessage(self.jinja2, provider)
                    
                    # Provider is Activated
                    # login automatically
                    self.login_user(provider.email, password)
                
                    # TODO Add Welcome Message and invitation to review profile and set schedule
                    #redirect_url = provider.get_edit_link(section='profile')
                    #self.redirect(redirect_url)
                
                    welcome_message = _("Welcome to Clikcare! Please review your profile and open your schedule.")
                    ProviderBaseHandler.render_bookings(self, provider, success_message=welcome_message)
                
            # something went wrong, user not created
            else:
                logging.error('(PasswordHandler.post) User not created. Probably because email already in Unique table.')
                    
                # TODO add custom validation to tell user that email is already in use.
                error_message = 'User email is already taken. If you are already using this email for your patient profile, please inform us or use another email.'
                self.render_password_selection(provider, password_form=password_form, error_message=error_message)
        
        # password form was not validate, re-render and try again!
        else:
            self.render_password_selection(provider, password_form=password_form)

        
class ActivationHandler(UserBaseHandler):
    def get(self, signup_token=None):
        if signup_token:
            user = self.validate_signup_token(signup_token)
            if user:
            
                if auth.PROVIDER_ROLE in user.roles:
                    provider = db.get_provider_from_user(user)
                
                    if provider:
                        # mark terms as not agreed
                        provider.terms_agreement = False
                        provider.terms_date = None

                        # show terms page
                        terms_form = ProviderTermsForm(obj=provider)
                        self.render_terms(provider, terms_form=terms_form)
                    else:
                        # no provider found for user & token combination, send them to the login page
                        logging.info('(ActivationHandler) no provider found for user & token combination')
                        self.redirect("/login")
                        
            else:
                # no user found for token combination, send them to the login page
                logging.info('(ActivationHandler) no user found for signup token %s' % signup_token)
                self.redirect("/login")

        else:
            logging.info('(ActivationHandler) No signup token in request')
            self.redirect("/login")

          
class ProviderSignupHandler(UserBaseHandler):
    def post(self):
        provider_email = self.request.get('provider_email')
        provider_postalcode = self.request.get('provider_postalcode')

        message = "Received sign-up request from email->%s postal_code->%s" % (provider_email, provider_postalcode)

        logging.info(message)

        from_email = "cliktester@gmail.com"
        subject = "Request for signup from provider"

        mail.email_contact_form(self.jinja2, from_email, subject, message)

        success_message = 'Thanks for your interest. We will be in touch soon!'
        self.render_template('login.html', form=LoginForm(), success_message=success_message)
        
        

class LoginHandler(BaseHandler):
    '''
        GET shows login page
        POST checks username, password, logs in user and redirect to start page
    '''
    def get(self):
        ''' Show login page '''
        
        self.render_template('login.html', form=LoginForm())

    def post(self):
        ''' checks username, password, logs in user and redirect to start page '''
        
        login_form = LoginForm(self.request.POST)
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
                        logging.info('(LoginHandler.post) User %s logged in as provider, redirecting to bookings page', user.get_email())

                        self.redirect(provider.get_edit_link('/provider/bookings'))

                    elif auth.PATIENT_ROLE in user.roles:
                        # patient = db.get_patient_from_user(user)
                        # no welcome page for patient yet!
                        
                        logging.info('(LoginHandler.post) User %s logged in as patient, redirecting to / page', user.get_email())
                        self.redirect('/')
                        
                    else:
                        logging.error('(LoginHandler.post) User %s logged in without roles', user.get_email())
                        error_message = 'Your account is not activated. Please check your email for an activation message or <a href="/contact">contact us</a> if you require assistance.'
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
        user = self.get_current_user()
        if user:
            logging.info("(LogoutHandler.get) Logging out user: %s" % user.get_email())

        self.auth.unset_session()
        self.redirect('/')

