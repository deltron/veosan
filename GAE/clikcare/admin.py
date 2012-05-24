'''
    admin handlers
'''

from google.appengine.ext import db as gdb
from google.appengine.api import users
from base import BaseHandler
import data.db as db, mail
import logging
from data.model import Provider
import random, sha, urlparse


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
        self.render_providers()
                  
class NewProviderInitHandler(AdminBaseHandler):
    '''
        Create a unique ID for the new provider, initalize profile with defaults.
        This allows the admin to login with their ID to fill out and customize the profile
    '''
    def post(self):
        provider_email = self.request.get('providerEmail')
        provider_key = db.initProvider(provider_email)
        provider = provider_key.get()
        logging.info('initialized new provider with key : %s' % provider_key)
        success_message = 'Initialized new provider for %s' % (provider_email)
        self.render_providers(success_message=success_message)
        
        
class NewProviderSolicitHandler(BaseHandler):
    '''
        Assumes profile has been completed to admin's satisfaction, now send out
        the sollicitation email to the provider to reset password and agree to terms.
    '''
    def post(self):
        key = self.request.get('provider_key')
        if (key):
            # edit provider
            provider = Provider.get(key)
            # create and store activation key and url
            salt = sha.new(str(random.random())).hexdigest()[:5]
            activation_key = sha.new(salt + provider.first_name + provider.last_name).hexdigest()
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
            logging.info("Missing key")
            
