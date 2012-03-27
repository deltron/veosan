'''
    admin handlers
'''

from google.appengine.ext import db
from base import BaseHandler

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