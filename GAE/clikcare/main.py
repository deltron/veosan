# -*- coding: utf-8 -*-

# GAE
import webapp2, logging
from google.appengine.api import users
from webapp2 import Route
# clik
import admin, util, db, provider, mail
from base import BaseHandler
from forms import BookingForm, PatientForm, ContactForm
from data import Booking


class BaseBookingHandler(BaseHandler):
    '''Common functions for all booking handlers'''
    
    def renderConfirmedBooking(self, booking):
        tv = {'patient': booking.patient, 'booking': booking, 'provider': booking.provider}
        self.render_template('patient/book.html', **tv)
        
    def renderNewPatientForm(self, patientForm, booking):
        tv = {'form': patientForm, 'booking': booking, 'provider': booking.provider}
        self.render_template('patient/new.html', **tv)
                
    
class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('index.html', form=BookingForm(self.request.GET))
        
    def post(self):
        ''' Renders 2nd page: Result + Confirm button
            This handler is slightly confusing, because we are processing a POST at /, but rendering a /patient/book page
        '''
        bookingform = BookingForm(self.request.POST)
        if bookingform.validate():
            booking = db.storeBooking(self.request.POST, None, None)
            logging.debug('Created booking:' + unicode(booking.key()))
            logging.info("Looking for best provider...")
            provider = db.findBestProviderForBooking(booking)
            if (provider):
                logging.info("Provider found: " + provider.fullName())
                booking.provider = provider
                booking.dateTime = booking.requestDateTime
                booking.put()
                # booking saved with provider, we need to get patient info
            else:
                logging.warn('No provider found for booking:' + unicode(booking.key()))
            
            tv = {
                  'patient': None, 'booking': booking, 'provider': provider }    
            self.render_template('patient/book.html', **tv) 
        else:
            self.render_template('index.html', form=bookingform)
    

class StaticHandler(BaseHandler):
    def get(self):
        template = "static/" + self.request.route.name + ".html"
        self.render_template(template)
        

class ContactHandler(BaseHandler):
    def get(self):
        self.render_template("contact.html", form=ContactForm(self.request.GET), sent=False)

    def post(self):
        contact_form = ContactForm(self.request.POST)
        if contact_form.validate():
            from_email = contact_form.email.data
            subject = contact_form.subject.data
            message = contact_form.message.data
            
            # send email
            # show confirmation page
            
            logging.info('Feedback from %s | subject: %s\n\nMESSAGE\n=========\n%s' % (from_email, subject, message))
            
            self.render_template('contact.html', form=contact_form, sent=True)
        else:
            self.render_template('contact.html', form=contact_form, sent=False)

 
class PatientBookHandler(BaseBookingHandler):
    def get(self):
        'We have a booking with a provider, we need to add the patient using the OpenID User'
        booking_key = self.request.get('bk')
        booking = Booking.get(booking_key)
        # get patient from user
        user = users.get_current_user()
        if (user):
            logging.info('User:' + str(user.__dict__))
            patient = db.getPatientFromUser(user)
            if (patient):
                logging.info('Patient exists, confirming booking.')
                booking.patient = patient
                booking.put()
                self.renderConfirmedBooking(booking)
            else:
                logging.info('Patient does not exist, creating new patient.')
                patientForm = PatientForm(self.request.POST)
                # set email in form from openID user
                patientForm.email.data = user.email()
                self.renderNewPatientForm(patientForm, booking)
        else:
            logging.info('User not logged in.')
    
    def post(self):
        '''This handler is for the New Patient Form'''
        # create patient form for validation
        patientForm = PatientForm(self.request.POST)
        # fetch booking from bk
        booking_key = self.request.get('bk')
        logging.info('Fetching booking:' + str(booking_key))
        booking = Booking.get(booking_key)
        if patientForm.validate():
            # Store New Patient 
            user = users.get_current_user()
            patient = db.storePatient(self.request.POST, user)
            if (patient):
                booking.patient = patient
                booking.put()
                # booking succesfull, send email
                mail.emailBooking(booking)
            else:
                logging.info("No booking saved because patient is None")
            self.renderConfirmedBooking(booking)
        else:           
            self.renderNewPatientForm(patientForm, booking)



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
                                       # General pages
                                       ('/', IndexHandler),
                                       ('/contact', ContactHandler),
                                       
                                       # Static Pages
                                       Route('/about', handler=StaticHandler, name='about'),
                                       Route('/careers', handler=StaticHandler, name='careers'),
                                       Route('/terms', handler=StaticHandler, name='terms'),
                                       Route('/privacy', handler=StaticHandler, name='privacy'),
                                       
                                       # Patient
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

