'''
    admin handlers
'''

from google.appengine.ext import db as gdb
from google.appengine.api import mail
from base import BaseHandler
import db
import logging
from data import Provider


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
        bookings = gdb.GqlQuery("SELECT * FROM Booking ORDER BY createdOn DESC LIMIT 10")
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
        provider = Provider.get(provider_key)
        logging.info('initialized new provider with key : %s' % provider_key)
        success_message = 'Initialized new provider for %s' % (provider_email)
        self.render_providers(success_message=success_message)
        
        
class NewProviderSolicitHandler(BaseHandler):
    '''
        Assumes profile has been completed to admin's satisfaction, now send out
        the sollicitation email to the provider to reset password and agree to terms.
    '''
    def post(self):
        # user_address = self.request.get("email_address")
        user_address = "leblancd@gmail.com" #hardcode for now
        if not mail.is_email_valid(user_address):
            #  some error message
            logging.info('invalid email address : %s' % user_address)
        else:
            confirmation_url = "http://www.google.com"
            sender_address = "cliksante.com <mail@cliksante.com>"
            subject = "Confirm your profile"
            body = """
Thank you for creating an account!  Please confirm your email address by
clicking on the link below:

%s
""" % confirmation_url

            mail.send_mail(sender_address, user_address, subject, body)
            self.render_template('admin/adminindex.html')