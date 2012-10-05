from handler.admin import AdminBaseHandler
from data import db
from handler.auth import admin_required
from google.appengine.ext import ndb


class AdminBookingsHandler(AdminBaseHandler):
    '''Administer Bookings'''
    
    @admin_required
    def get(self):
        bookings = db.fetch_bookings()
        self.render_template('admin/admin_bookings.html', bookings=bookings)


class AdminBookingDetailHandler(AdminBaseHandler):
    '''Administer a single Booking'''
    
    @admin_required
    def get(self, operation, booking_key):
        key = ndb.Key(urlsafe=booking_key)
        booking = key.get()
        
        if operation == 'show':
            self.render_template('admin/admin_booking_detail.html', booking=booking)
        elif operation == 'cancel':
            booking.cancelled = True
            booking.put()
            self.render_template('admin/admin_booking_detail.html', booking=booking, success_message='Booking canceled.')
        elif operation == 'reactivate':
            booking.cancelled = False
            booking.put()
            self.render_template('admin/admin_booking_detail.html', booking=booking, success_message='Booking reactivated.')
        