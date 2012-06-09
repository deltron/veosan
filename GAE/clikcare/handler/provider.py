import logging, random, sha, urlparse
from datetime import date
#clik
from base import BaseHandler
import data.db as db
from forms.provider import ProviderTermsForm, ProviderPasswordForm
from forms.login import LoginForm
from data.model import Schedule
import util
import mail
from handler.auth import provider_required
from webapp2_extras.i18n import gettext as _
from webapp2_extras import security 

class ProviderBaseHandler(BaseHandler):       
    def render_schedule(self, provider, availableIds, **extra):
        timeslots = util.getScheduleTimeslots()
        days = util.getWeekdays()
        self.render_template('provider/schedule.html', provider=provider, availableIds=availableIds, timeslots=timeslots, days=days, **extra)
    
    def render_bookings(self, provider, **extra):
        bookings = db.fetch_future_bookings(provider)   
        logging.info('Bookings:' + str(bookings))
        self.render_template('provider/bookings.html', provider=provider, bookings=bookings, **extra)
            
    def render_terms(self, provider, terms_form, **extra):
        self.render_template('provider/provider_terms.html', provider=provider, form=terms_form, **extra)

    def render_password_selection(self, provider, password_form=None, **extra):
        if not password_form:
            password_form = ProviderPasswordForm()
        self.render_template('provider/password.html', provider=provider, form=password_form, **extra)
        

class ProviderScheduleHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        availableIds = provider.getAvailableScheduleIds()
        logging.info('available ids' + str(availableIds))
        self.render_schedule(provider, availableIds)
           
    @provider_required
    def post(self):
        logging.info('ProviderScheduleHandler POST')
        urlsafe_key = self.request.get('key')
        day_time = self.request.get('day_time')
        day, startTime, endTime = day_time.split('-')
        operation = self.request.get('operation')
        logging.info("SAVE SCHEDULE: " + urlsafe_key + " " + day + "-" + startTime + "-" + endTime + " " + operation)
        
        provider = db.get_from_urlsafe_key(urlsafe_key)
        if (operation == 'add'):
            s = Schedule()
            s.provider = provider.key
            s.day = int(day)
            s.startTime = int(startTime)
            s.endTime = int(endTime)
            new_schedule_key = s.put()
            logging.info('New Schedule saved: %s' % new_schedule_key)
        elif (operation == 'remove'):
            schedule_to_delete = Schedule.query(Schedule.provider == provider.key, Schedule.day == int(day), Schedule.startTime == int(startTime)).get()
            logging.info('deleting schedule' + str(schedule_to_delete))
            if (schedule_to_delete):
                schedule_to_delete.key.delete()
            else:
                logging.error("Can't find schedule to delete")  
        else:
            logging.info('Wrong operation save schedule:' + operation)

class ProviderTermsHandler(ProviderBaseHandler):
    def get(self):
        # get the provider key
        key = self.request.get('key')
        if key:
            provider = db.get_from_urlsafe_key(key)
        
        # if no key, try to find out who the provider is by checking the logged in user
        else:
            user = self.get_current_user()
            # make sure user is a provider
            if 'provider' in user.roles:
                provider = db.get_provider_from_email(user.get_email())
        
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

class ProviderResetPasswordHandler(ProviderBaseHandler):
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


class ProviderPasswordHandler(ProviderBaseHandler):
    def get(self):
        '''
            TODO: Display page in the context of the Provider profile (with tabs at the top)
        '''
        logging.info('GET not implemented on /provider/password')
        self.redirect("/")
            
    def post(self):
        '''
            Create user and link it to the Provider
        '''

        password_form = ProviderPasswordForm(self.request.POST)
                            
        # get provider from request
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        
        if password_form.validate():
            # get password from request
            password = self.request.get('password')
            
            # get user from provider
            user = db.get_user_from_email(provider.email)
            
            # check if user exists, if yes then we are just setting a new password
            if user:            
                # set password (same as passing password_raw to user_create)
                password_hash = security.generate_password_hash(password, length=12)    
                user.password = password_hash
                user.put()
                
                # clear the password reset key from provider to prevent further shenanigans
                provider.resetpassword_key = None
                provider.put()
                
                logging.info('(ProviderPasswordHandler.post) Set new password for email %s' % provider.email)

                self.login_user(provider.email, password)

                success_message = _("Welcome back! Password has been reset for %s" % provider.email)
                self.render_bookings(provider, success_message=success_message)

            # user doesn't exist, let's make a new one, set the password and link to provider
            else:
                logging.info('(ProviderPasswordHandler.post) Creating a new user for %s' % provider.email)
                
                # add provider role to user
                roles = ['provider']
        
                # create and store the user
                user = self.create_user(provider.email, password, roles)
        
                # if user created successfully, link to to the provider
                if user:
                    # Link user to provider and save
                    provider.user = user.key
                
                    # remove activation link from user
                    provider.activation_key = None

                    # save provider
                    provider.put()
            
                    logging.info('(ProviderPasswordHandler.post) Provider<->User linked for %s' % provider.email)

            
                    # send welcome email
                    mail.emailProviderWelcomeMessage(self.jinja2, provider)
            
                    # Provider is Activated
                    # login automatically
                    self.login_user(provider.email, password)
                
                    # TODO Add Welcome Message and invitation to review profile and set schedule
                    #redirect_url = provider.get_edit_link(section='profile')
                    #self.redirect(redirect_url)
                
                    welcome_message = _("Welcome to Clikcare! Please review your profile and open your schedule.")
                    self.render_bookings(provider, success_message=welcome_message)
                
                # something went wrong, user not created
                else:
                    logging.error('(ProviderPasswordHandler.post) User not created. Probably because email already in Unique table.')
                    
                    # TODO add custom validation to tell user that email is already in use.
                    error_message = 'User email is already taken. If you are already using this email for your patient profile, please inform us or use another email.'
                    self.render_password_selection(provider, password_form=password_form, error_message=error_message)
        
        # password form was not validate, re-render and try again!
        else:
            self.render_password_selection(provider, password_form=password_form)


class ProviderBookingsHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        
        self.render_bookings(provider)


        
class ProviderActivationHandler(ProviderBaseHandler):
    def get(self, activation_key=None):
        #parse URL to get activation key
        if (activation_key):
            provider = db.get_provider_from_activation_key(activation_key)
            
            if provider:
                # mark terms as not agreed
                provider.terms_agreement = False
                provider.terms_date = None
            
                # show terms page
                terms_form = ProviderTermsForm(obj=provider)
                self.render_terms(provider, terms_form=terms_form)
            else:
                # no provider found for activation key, send them to the login page
                self.redirect("/login")
        else:
            logging.info('No activation key')
            

class ProviderSignupHandler(ProviderBaseHandler):
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
