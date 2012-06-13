'''
    admin handlers
'''

import logging, urlparse

# clik
from forms.admin import NewProviderForm
from base import BaseHandler
import data.db as db, mail
from handler.auth import admin_required


class AdminBaseHandler(BaseHandler):
    ''' Base functions for administration pages''' 

    def render_providers(self, **tv):
        providers = db.fetchProviders()
        self.render_template('admin/admin_providers.html', providers=providers, **tv)

class AdminIndexHandler(AdminBaseHandler):
    '''Administration Index'''

    @admin_required
    def get(self):
        self.redirect('/admin/bookings')


class AdminBookingsHandler(AdminBaseHandler):
    '''Administer Bookings'''
    
    @admin_required
    def get(self):
            bookings = db.fetch_bookings()
            self.render_template('admin/admin_bookings.html', bookings=bookings)


class AdminProvidersHandler(AdminBaseHandler):
    ''' Administer Providers '''
 
    @admin_required
    def get(self):
        self.render_providers(form=NewProviderForm())

                  
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
            
            # check if a provider exists with this address already
            existing_provider = db.get_provider_from_email(provider_email)
            if existing_provider:
                error_message = 'Provider already exists for email address: %s' % (provider_email)
                self.render_providers(error_message=error_message, form=form)        

            else:
                provider_key = db.initProvider(provider_email)
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
    
    def post(self):
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        
        # Check provider has at least a first name, last name and email before activation
        if provider.email and provider.first_name and provider.last_name:            
            # create a blank user with provider role
            user = self.create_empty_user_for_provider(provider)
            
            # create a signup token for new user
            token = self.create_signup_token(user)
            
            # activation url
            url_obj = urlparse.urlparse(self.request.url)
            activation_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/user/activation/' + token, '', '', ''))
            logging.info('(NewProviderSolicitHandler.post) generated activation url for user %s : %s ' %  (provider.email, activation_url))
            
            # send email
            mail.emailSolicitProvider(self.jinja2, provider, activation_url)
            
            # render the provider admin page
            success_message='Solicit email sent to %s' % provider.email
            self.render_template('provider/administration.html', provider=provider, success_message=success_message)
        else:
            error_message='Incomplete profile for %s, email not sent' % provider.email
            self.render_template('provider/administration.html', provider=provider, error_message=error_message)

