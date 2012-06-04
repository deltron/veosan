'''
    admin handlers
'''

import logging, random, sha, urlparse

# clik
from data.model import Provider
from forms.admin import NewProviderForm
from base import BaseHandler
import data.db as db, mail


class AdminBaseHandler(BaseHandler):
    ''' Base functions for administration pages''' 
    def render_providers(self, **tv):
        providers = db.fetchProviders()
        self.render_template('admin/admin_providers.html', providers=providers, **tv)

class AdminIndexHandler(AdminBaseHandler):
    '''Administration Index'''

    def get(self):
        self.redirect('/admin/bookings')

class AdminBookingsHandler(AdminBaseHandler):
    '''Administer Bookings'''
    def get(self):
            bookings = db.fetch_bookings()
            self.render_template('admin/admin_bookings.html', bookings=bookings)

class AdminProvidersHandler(AdminBaseHandler):
    ''' Administer Providers '''
 
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
            provider_key = db.initProvider(provider_email)
            logging.info('initialized new provider with key : %s' % provider_key)
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
        # create and store activation key and url
        salt = sha.new(str(random.random())).hexdigest()[:5]
        
        # Check provider has at least a first name, last name and email before activation
        if provider.email and provider.first_name and provider.last_name:
            activation_key = sha.new(salt + provider.email + provider.first_name + provider.last_name).hexdigest()
            provider.activation_key = activation_key
            provider.put()
            
            # activation url
            url_obj = urlparse.urlparse(self.request.url)
            activation_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/provider/activation/' + provider.activation_key, '', '', ''))
            logging.info('activation url:' + activation_url)
            
            # send email
            mail.emailSolicitProvider(self.jinja2, provider, activation_url)
            
            # render the provider admin page
            success_message='Solicit email sent to %s' % provider.email
            self.render_template('provider/administration.html', p=provider, success_message=success_message)
        else:
            error_message='Incomplete profile for %s, email not sent' % provider.email
            self.render_template('provider/administration.html', p=provider, error_message=error_message)

