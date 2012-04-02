# -*- coding: utf-8 -*-

import webapp2
import util
import logging
from base import BaseHandler
import admin
import db
from forms import BookingForm, PatientForm
import provider
from pytz.gae import pytz

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('index.html', form=BookingForm(self.request.GET))
        
    def post(self):
        form = BookingForm(self.request.POST)
        if form.validate():
            logging.info('booking post:' + unicode(self.request))
            booking_key = db.storeBooking(self.request)
            booking_key_string = unicode(booking_key)
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
jinja_filters['formatdate'] = util.formatDate
jinja_filters['formatdatetime_noseconds'] = util.formatDateTimeNoSeconds
jinja_filters['format_hour'] = util.format_hour
jinja_filters['format_30min_period'] = util.format_30min_period
jinja_filters['dump'] = util.dump

jinja_environment_args = {
        'autoescape': True,
        'extensions': [
            'jinja2.ext.autoescape',
            'jinja2.ext.with_',
            'jinja2.ext.i18n'   
        ]}


webapp2_config = {}
webapp2_config['webapp2_extras.jinja2'] = {
                                            'filters': jinja_filters,
                                            'environment_args': jinja_environment_args
                                            } 

webapp2_config['webapp2_extras.i18n'] = {
                                         'translations_path': 'locale',
                                         'default_locale': 'fr'
                                         }
application = webapp2.WSGIApplication([
                                       ('/', IndexHandler),
                                       ('/patient/book', PatientBookHandler),
                                       # provider
                                       ('/provider/profile', provider.ProviderEditProfileHandler),
                                       ('/provider/address', provider.ProviderEditAddressHandler),
                                       ('/provider/address/upload', provider.ProviderAddressUploadHandler),
                                       ('/provider/schedule', provider.ProviderScheduleHandler),
                                       ('/provider/terms', provider.ProviderTermsHandler),
                                       ('/serve/([^/]+)?', provider.ServeHandler), # temporary - to test file uploads
                                       # admin
                                       ('/admin/provider/init', admin.NewProviderInitHandler),
                                       ('/admin/provider/solicit', admin.NewProviderSolicitHandler),
                                       ('/admin', admin.AdminIndexHandler),
                                       ('/admin/bookings', admin.AdminBookingsHandler),
                                       ('/admin/providers', admin.AdminProvidersHandler) 
                                      ], debug=True,
                                      config=webapp2_config)

