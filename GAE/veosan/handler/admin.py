'''
    admin handlers
'''

import logging, urlparse

# veo
from forms.admin import NewProviderForm
from base import BaseHandler
import data.db as db, mail
from data.model import SiteConfig
import util
from handler.auth import admin_required
from google.appengine.ext import ndb
from handler.provider_admin import ProviderAdminBaseHandler



class AdminBaseHandler(BaseHandler):
    ''' Base functions for administration pages''' 

    def render_providers(self, **kw):
        providers = db.fetch_providers()
        self.render_template('admin/admin_providers.html', providers=providers, **kw)

    def render_data(self, **kw):
        dev_server = util.is_dev_server(self.request)
        site_config = db.get_site_config()
        
        logging.info('(AdminBaseHandler.render_data) dev_server=%s' % dev_server)
        self.render_template('admin/data.html', dev_server=dev_server, site_config=site_config, **kw)

class AdminIndexHandler(AdminBaseHandler):
    '''Administration Index'''

    @admin_required
    def get(self):
        self.redirect('/admin/providers')


class AdminSiteConfigHandler(AdminBaseHandler):
    def post(self, feature=None):
        
        # validate features that can be switched
        if feature in ['booking_enabled', 'google_analytics_enabled']:            
            site_config = db.get_site_config()

            # toggle state
            current_state = getattr(site_config, feature)
            
            if current_state:           
                setattr(site_config, feature, False)
                success_message = 'feature %s is now set to %s' % (feature, False)
                    
            else:
                setattr(site_config, feature, True)
                success_message = 'feature %s is now set to %s' % (feature, True)

            site_config.put()
            
            self.render_data(success_message=success_message)

        else:
            logging.error('Received unknown feature switch : %s' % feature)




class AdminBookingsHandler(AdminBaseHandler):
    '''Administer Bookings'''
    
    @admin_required
    def get(self):
        bookings = db.fetch_bookings()
        self.render_template('admin/admin_bookings.html', bookings=bookings)


class AdminBookingDetailHandler(AdminBaseHandler):
    '''Administer a single Booking'''
    
    @admin_required
    def get(self, operation, bk):
        booking = db.get_from_urlsafe_key(bk)
        if operation == 'show':
            self.render_template('admin/admin_booking_detail.html', b=booking)
        elif operation == 'cancel':
            booking.status = 'canceled'
            booking.put()
            self.render_template('admin/admin_booking_detail.html', b=booking, success_message='Booking canceled.')
        elif operation == 'reactivate':
            booking.status = 'active'
            booking.put()
            self.render_template('admin/admin_booking_detail.html', b=booking, success_message='Booking reactivated.')
        

class AdminProvidersHandler(AdminBaseHandler):
    ''' Administer Providers '''
 
    @admin_required
    def get(self):
        self.render_providers(form=NewProviderForm())
        
class AdminPatientsHandler(AdminBaseHandler):
    ''' Administer Patients '''
 
    @admin_required
    def get(self):
        patients = db.fetch_patients()
        self.render_template('admin/patients.html', patients=patients)

                  
class NewProviderInitHandler(AdminBaseHandler):
    '''
        Create a unique ID for the new provider, initalize profile with defaults.
        This allows the admin to login with their ID to fill out and customize the profile
    '''

    def post(self):
        form = NewProviderForm(self.request.POST)
        if form.validate():
            # Init Provider
            provider_email = self.request.get('provider_email')
            vanity_url = self.request.get('vanity_url')
            
            # force the vanity URL to lowercase
            vanity_url = vanity_url.lower()

            provider_key = db.init_provider(provider_email, vanity_url)
            logging.info('(NewProviderInitHandler.post) initialized new provider with key : %s' % provider_key)
            success_message = 'Initialized new provider for %s' % (provider_email)
            self.render_providers(success_message=success_message, form=form)        
        else:
            # show error
            logging.info('Trying to create a provider with invalid email address: %s' % form.provider_email)
            self.render_providers(form=form)
        
        
class NewProviderSolicitHandler(BaseHandler):
    '''
        Assumes profile has been completed to admin's satisfaction, now send out
        the sollicitation email to the provider to reset password and agree to terms.
    '''
    
    @admin_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        # Check provider has at least a first name, last name and email before activation
        if provider.email: 
            # create a blank user with provider role
            if provider.user: 
                user = provider.user.get()
            else:    
                user = self.create_empty_user_for_provider(provider)
            
            # create a signup token for new user
            token = self.create_signup_token(user)
            
            # activation url
            url_obj = urlparse.urlparse(self.request.url)
            activation_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/user/activation/' + token, '', '', ''))
            logging.info('(NewProviderSolicitHandler.post) generated activation url for user %s : %s ' % (provider.email, activation_url))
            
            # send email
            mail.emailSolicitProvider(self.jinja2, provider, activation_url)
            
            # render the provider admin page
            success_message = 'Solicit email sent to %s' % provider.email
            ProviderAdminBaseHandler.render_administration(self, provider=provider, success_message=success_message)
        else:
            error_message = 'Incomplete profile for %s, email not sent' % provider.email
            ProviderAdminBaseHandler.render_administration(self, provider=provider, error_message=error_message)


class AdminDataHandler(AdminBaseHandler):
    ''' Administer Providers '''

    def get(self):        
        self.render_data()


class AdminStageDataHandler(AdminBaseHandler):
    ''' Administer Providers '''

    def post(self):
        if util.is_dev_server(self.request):
            logging.info('*** Generating test data for providers')
            from data import test_data
            test_data.create_test_providers()
            self.render_data(success_message="Generated provider data successfully")

        else:
            logging.info('*** Someone tried to Generating test data for providers on a production server. WTF!?')
            self.render_data(error_message="Production server, cannot generate test provider data")

class AdminDeleteDataHandler(AdminBaseHandler):
    ''' Delete all data from database '''

    def post(self):
        logging.info('self.request.host %s' % self.request.host)
        
        if util.is_dev_server(self.request):
            confirm_text = self.request.get('confirm_text')
            if confirm_text == 'delete':
                all_entities = ndb.Query().fetch(keys_only=True)
                logging.info('*** DELETE ALL ENTITIES: %s' % all_entities)
                for e in all_entities: 
                    e.delete()
                self.render_data(success_message="Everything deleted")
            else:
                self.render_data(error_message="Missing confirmation code")

        else:
            logging.info('*** Someone tried to delete everything from a production server. WTF!?')
            self.render_data(error_message="Production server, cannot delete")



        
