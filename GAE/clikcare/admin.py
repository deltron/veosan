'''
    admin handlers
'''

from google.appengine.ext import db
from google.appengine.api import mail
from base import BaseHandler
import logging

class IndexHandler(BaseHandler):
    '''
        Admin Index
    '''
    def get(self):
        bookings = db.GqlQuery("SELECT * FROM Booking ORDER BY createdOn DESC LIMIT 10")
        providers = db.GqlQuery("SELECT * from Provider ORDER BY lastName ASC LIMIT 50")
        tv = {
              'bookings': bookings,
              'providers': providers 
              }    
        self.render_template('admin/adminindex.html', **tv)
        
        
        
class NewProviderInitHandler(BaseHandler):
    '''
        Create a unique ID for the new provider, initalize profile with defaults.
        
        This allows the admin to login with their ID to fill out and customize the profile
    '''
    def get(self):
        logging.info('initialize new provider with id : %s' % u'1234')
        self.render_template('admin/adminindex.html')        
        
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