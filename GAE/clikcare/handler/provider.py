# -*- coding: utf-8 -*-
import logging
from datetime import date
# GAE
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
#clik
from base import BaseHandler
import data.db as db
from forms.provider import ProviderTermsForm, ProviderPasswordForm
from data.model import Provider, Schedule
import util, mail
from handler.auth import provider_required

class ProviderBaseHandler(BaseHandler):       
    def render_schedule(self, provider, availableIds, **extra):
        timeslots = util.getScheduleTimeslots()
        days = util.getWeekdays()
        self.render_template('provider/schedule.html', p=provider, availableIds=availableIds, timeslots=timeslots, days=days, **extra)
    
    def render_bookings(self, provider, **extra):
        bookings = db.fetch_future_bookings(provider)   
        logging.info('Bookings:' + str(bookings))
        self.render_template('provider/bookings.html', p=provider, bookings=bookings, **extra)
            
    def render_terms(self, provider, terms_form, **extra):
        self.render_template('provider/provider_terms.html', p=provider, form=terms_form, **extra)

    def render_password_selection(self, provider, password_form=None, **extra):
        if not password_form:
            password_form = ProviderPasswordForm()
        self.render_template('provider/password.html', p=provider, form=password_form, **extra)
        

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
        urlsafe_key = self.request.get('provider_key')
        day_time = self.request.get('day_time')
        day, startTime, endTime = day_time.split('-')
        operation = self.request.get('operation')
        logging.info("SAVE SCHEDULE: " + urlsafe_key + " " + day + "-" + startTime + "-" + endTime + " " + operation)
        
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
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


class ProviderPasswordHandler(ProviderBaseHandler):
    def get(self):
        '''
            TODO: Display page in the context of the Provider profile (with tabs at the top)
        '''
        logging.info('GET not implemented on /provider/password')
        pass
            
    def post(self):
        '''
            Create user and link it to the Provider
        '''
        logging.info('POST provider password')
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        password_form = ProviderPasswordForm(self.request.POST)
        if password_form.validate():
            # Create User in Auth system
        
            # get email from provider, we are not reading email from the form
            email = provider.email
        
            # get password from request
            password = self.request.get('password')
        
            # add provider role to user
            roles = ['provider']
        
            # create and store the user
            user = self.create_user(email, password, roles)
        
            if user:
                # Link user to provider and save
                provider.user = user.key
                
                # remove activation link from user
                provider.activation_key = None

                # save provider
                provider.put()
            
                # send welcome email
                mail.emailProviderWelcomeMessage(self.jinja2, provider)
            
                # Provider is Activated
                # login automatically
                self.login_user(email, password)
                # TODO Add Welcome Message and invitation to review profile and set schedule
                #redirect_url = provider.get_edit_link(section='profile')
                #self.redirect(redirect_url)
                
                welcome_message = _("Welcome to Clikcare! Please review your profile and open your schedule.")
                self.render_bookings(provider, success_message=welcome_message)
            else:
                logging.error('User not created. Probably because email already in Unique table.')
                # TODO add custom validation to tell user that email is already in use.
                error_message = 'User email is already taken. If you are already using this email for your patient profile, please inform us or use another email.'
                self.render_password_selection(provider, password_form=password_form, error_message=error_message)
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

        self.redirect("/")
