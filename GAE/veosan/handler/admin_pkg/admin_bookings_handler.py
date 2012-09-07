from handler.admin import AdminBaseHandler
from data import db
from handler.auth import admin_required


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
        