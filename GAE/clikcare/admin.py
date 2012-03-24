'''
    admin handlers
'''

from google.appengine.ext import db
from base import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        
        bookings = db.GqlQuery("SELECT * FROM Booking ORDER BY createdOn DESC LIMIT 10")

        tv = { 'bookings': bookings }
        
        self.render_template('admin/adminindex.html', **tv)