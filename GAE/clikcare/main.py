# -*- coding: utf-8 -*-
import webapp2
import util
import logging
from base import BaseHandler
import admin
import db
from forms import BookingForm, PatientForm
import provider


class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('index.html', form=BookingForm(self.request.GET))
        
    def post(self):
        form = BookingForm(self.request.POST)
        if form.validate():
            logging.info('booking post:' + str(self.request))
            booking_key = db.storeBooking(self.request)
            booking_key_string = str(booking_key)
            logging.info('created booking:' + booking_key_string)
            #self.request.POST['booking'] = booking_key_string
            tv = {
                  'form': PatientForm(self.request.POST),
                  'booking': booking_key_string
                  }
            self.render_template('patient/new.html', **tv)
        else:
            self.render_template('index.html', form=form)

    
class PatientBookHandler(BaseHandler):
    def post(self):
        form = PatientForm(self.request.POST)
        if form.validate():
            logging.info('patient post:' + str(self.request))
            # Store Patient liked to Booking
            db.storePatient(self.request)
            self.render_template('patient/book.html', form=form) 
        else:
            self.render_template('patient/new.html', form=form)



jinja_filters = {}
jinja_filters['formatdate'] = util.formatDateFR
jinja_filters['formatdatetime_noseconds'] = util.formatDateTimeNoSeconds

webapp2_config = {}
webapp2_config['webapp2_extras.jinja2'] = {
                                            'filters': jinja_filters
                                            } 
application = webapp2.WSGIApplication([
                                       ('/', IndexHandler),
                                       ('/patient/book', PatientBookHandler),
                                       ('/provider/schedule', provider.ProviderScheduleHandler),
                                       ('/provider/address', provider.ProviderAddressHandler),
                                       ('/provider/address/upload', provider.ProviderAddressUploadHandler),
                                       ('/provider/profile', provider.ProviderProfileHandler),
                                       ('/provider/terms', provider.ProviderTermsHandler),
                                       ('/serve/([^/]+)?', provider.ServeHandler), # temporary - to test file uploads
                                       ('/admin', admin.IndexHandler)        
                                       ], debug=True,
                                      config=webapp2_config)
