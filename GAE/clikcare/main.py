# -*- coding: utf-8 -*-

# GAE
import webapp2, logging
# clik
import admin, util, db, provider, mail
from base import BaseHandler
from forms import BookingForm, PatientForm

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('index.html', form=BookingForm(self.request.GET))
        
    def post(self):
        bookingform = BookingForm(self.request.POST)
        if bookingform.validate():

            tv = {
                  'form': PatientForm(self.request.POST),
                  'bookingForm': bookingform
                  }
           
            self.render_template('patient/new.html', **tv)
        else:
            self.render_template('index.html', form=bookingform)

    
class PatientBookHandler(BaseHandler):
    def post(self):
        patientForm = PatientForm(self.request.POST)
        bookingForm = BookingForm(self.request.POST)

        if patientForm.validate():
            logging.debug('patientForm passed validation:' + str(self.request))
            # Store Patient 
            patient = db.storePatient(self.request.POST)
            if (patient):
                # Store booking without provider
                booking = db.storeBooking(self.request.POST, patient, None)
                logging.debug('created booking:' + unicode(booking.key()))
                # Implement magic to choose a provider...
                logging.info("Looking for best provider...")
                provider = db.findBestProviderForBooking(booking)
                if (provider):
                    logging.info("Provider found: " + provider.fullName())
                    booking.provider = provider
                    booking.put()
                    # booking succesfull, send email
                    mail.emailBooking(booking)
                else:
                    logging.warn('No provider found for booking:' + unicode(booking.key()))
            else:
                logging.info("No booking saved because patient is None")
            
            tv = {
                  'patient': patient,
                  'booking': booking,
                  'provider': provider
            }
            self.render_template('patient/book.html', **tv) 
        else:           
            tv = {
                  'form': patientForm ,
                  'bookingForm': bookingForm
                  }
            self.render_template('patient/new.html', **tv)



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
                                       ('/provider/login', provider.ProviderLoginHandler),
                                       ('/provider/profile', provider.ProviderEditProfileHandler),
                                       ('/provider/address', provider.ProviderEditAddressHandler),
                                       ('/provider/address/upload', provider.ProviderAddressUploadHandler),
                                       ('/provider/schedule', provider.ProviderScheduleHandler),
                                       ('/provider/terms', provider.ProviderTermsHandler),
                                       ('/provider/bookings', provider.ProviderBookingsHandler),
                                       ('/serve/([^/]+)?', provider.ServeHandler), # temporary - to test file uploads
                                       # admin
                                       ('/admin/provider/init', admin.NewProviderInitHandler),
                                       ('/admin/provider/solicit', admin.NewProviderSolicitHandler),
                                       ('/admin', admin.AdminIndexHandler),
                                       ('/admin/bookings', admin.AdminBookingsHandler),
                                       ('/admin/providers', admin.AdminProvidersHandler) 
                                      ], debug=True,
                                      config=webapp2_config)

