# -*- coding: utf-8 -*-

# GAE
import webapp2, logging
from google.appengine.api import users
from google.appengine.api.users import User
from webapp2 import Route
from webapp2_extras.routes import RedirectRoute
# clik
import admin, util, data.db as db, provider_handler, mail, auth_handler
from base import BaseHandler
from forms import BookingForm, PatientForm, ContactForm, EmailOnlyBookingForm
from data.model import Booking


class BaseBookingHandler(BaseHandler):
    '''Common functions for all booking handlers'''
    
    def renderConfirmedBooking(self, booking):
        tv = {'patient': booking.patient, 'booking': booking, 'provider': booking.provider}
        self.render_template('patient/book.html', **tv)
        
    def renderNewPatientForm(self, patientForm, booking):
        tv = {'form': patientForm, 'booking': booking, 'provider': booking.provider}
        self.render_template('patient/new.html', **tv)
        
    def renderFullyBooked(self, booking, emailForm=None):
        tv = {'booking': booking, 'form': emailForm}
        self.render_template('no_result.html', **tv) 
        
        
    
class IndexHandler(BaseBookingHandler):
    def get(self):
        self.render_template('index.html', form=BookingForm(self.request.GET))
        
    def post(self):
        ''' Renders 2nd page: Result + Confirm button
        TODO: Replace with passing booking properties and provider key, saving only after the patient logging ??? 
        '''
        bookingform = BookingForm(self.request.POST)
        if bookingform.validate():
            booking = db.storeBooking(self.request.POST, None, None)
            logging.debug('Created booking: %s' % booking.key)
            logging.info("Looking for best provider...")
            provider = db.findBestProviderForBooking(booking)
            if (provider):
                logging.info("Provider found: " + provider.fullName())
                booking.provider = provider.key
                booking.dateTime = booking.requestDateTime
                booking.put()
                # booking saved with provider, no patient info yet
                email_form = EmailOnlyBookingForm()
                tv = {'patient': None, 'booking': booking, 'p': provider, 'form': email_form }
                self.render_template('result.html', **tv) 
            else:
                logging.warn('No provider found for booking: %s' % booking.key.urlsafe())
                emailForm = EmailOnlyBookingForm()
                self.renderFullyBooked(booking, emailForm) 
        else:
            self.render_template('index.html', form=bookingform)


class FullyBookedHandler(BaseBookingHandler):
    def get(self):
        self.redirect
        
    def post(self):
        emailForm = EmailOnlyBookingForm(self.request.POST)
        booking_key = self.request.get('bk')
        booking = Booking.get(booking_key)
        if emailForm.validate():
            ''' Stores email for Booking with No Result'''
            booking.requestEmail = self.request.get('email')
            booking.put()
            self.renderFullyBooked(booking)
        else:
            self.renderFullyBooked(booking, emailForm)
        

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
    '''
        Handler to confirm the booking and create new patient record if user logged in
    '''
    def post(self):
        'We have a booking with a provider, we need to add the patient using the User'
        booking = db.get_from_urlsafe_key(self.request.get('bk')) 
        email_form = EmailOnlyBookingForm(self.request.POST)
        if email_form.validate():
            # store email in booking as requestEmail
            booking.request_email = self.request.get('email')
            booking.put()
            
            # TODO Consider case where user is already logged in
            
            # existing or new patient
            email = self.request.get('email')
            # if we know this email, send to login
            logging.info('email: %s' % email)
            existing_user = self.auth.store.user_model.get_by_auth_id(email)
            if existing_user:
                patient = db.getPatientFromUser(existing_user)
                if patient:
                    # Existing patient
                    logging.info('User exists, patient exists, confirming booking.')
                    booking.patient = patient
                    booking.put()
                    self.renderConfirmedBooking(booking)
                else:
                    # user exists, but not patient!!!
                    logging.error('User exists for %s but not patient' % email)
                    # TODO missing render call for this odd situation
            else:
                # New patient
                logging.info('Patient does not exist, creating new patient.')
                patientForm = PatientForm(self.request.POST)
                # set email in form 
                patientForm.email.data = email
                self.renderNewPatientForm(patientForm, booking)

        else:
            # email form validation failed
            tv = {'patient': None, 'booking': booking, 'p': booking.provider, 'form': email_form }
            self.render_template('result.html', **tv) 
            
            


class PatientBookForNewHandler(BaseBookingHandler):
    '''
        Handler for New Patient Form
    '''
    def post(self):
        logging.info('post to /patient/new')
        '''This handler is for the New Patient Form'''
        # create patient form for validation
        patientForm = PatientForm(self.request.POST)
        # fetch booking from bk
        booking_key = self.request.get('bk')
        logging.info('Fetching booking:' + str(booking_key))
        booking = Booking.get(booking_key)
        if patientForm.validate():
            # Create User in Auth system
            email = self.request.get('email')
            password = self.request.get('password')
            user = self.create_user(email, password)
            if user:
                # Store New Patient
                patient = db.storePatient(self.request.POST, user)
                if (patient):
                    booking.patient = patient
                    booking.put()
                    # booking succesfull, send email
                    mail.emailBookingToPatient(self.jinja2, booking)
                else:
                    logging.error("No booking saved because patient is None")
            else:
                logging.error('User not created.')
                # TODO add custom validation to tell user that email is already in use.
                self.renderNewPatientForm(patientForm, booking)
            self.renderConfirmedBooking(booking)
        else:           
            self.renderNewPatientForm(patientForm, booking)     




jinja_filters = {}
jinja_filters['format_date_weekday_after'] = util.format_date_weekday_after
jinja_filters['format_datetime_full'] = util.format_datetime_full
jinja_filters['format_datetime_noseconds'] = util.formatDateTimeNoSeconds
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

webapp2_config['webapp2_extras.sessions'] = {
                                             'secret_key': '82374y6ii899hy8-89308847-21u9x676',
                                             }

application = webapp2.WSGIApplication([
                                       # General pages
                                       ('/', IndexHandler),
                                       ('/full', FullyBookedHandler),
                                       ('/contact', ContactHandler),
                                       
                                       # Static Pages
                                       Route('/about', handler=StaticHandler, name='about'),
                                       Route('/careers', handler=StaticHandler, name='careers'),
                                       Route('/terms', handler=StaticHandler, name='terms'),
                                       Route('/privacy', handler=StaticHandler, name='privacy'),
                                       
                                       # Patient
                                       ('/patient/booknew', PatientBookForNewHandler),
                                       ('/patient/book', PatientBookHandler),
                                       
                                       # provider
                                       ('/provider/login', provider_handler.ProviderLoginHandler),
                                       ('/provider/profile', provider_handler.ProviderEditProfileHandler),
                                       ('/provider/address', provider_handler.ProviderEditAddressHandler),
                                       ('/provider/address/upload', provider_handler.ProviderAddressUploadHandler),
                                       ('/provider/schedule', provider_handler.ProviderScheduleHandler),
                                       ('/provider/terms', provider_handler.ProviderTermsHandler),
                                       ('/provider/bookings', provider_handler.ProviderBookingsHandler),
                                       ('/provider/administration', provider_handler.ProviderAdministrationHandler),
                                       Route('/provider/activation/<activation_key>', handler=provider_handler.ProviderActivationHandler),
                                       ('/serve/([^/]+)?', provider_handler.ServeHandler), # temporary - to test file uploads
                                       # admin
                                       ('/admin/provider/init', admin.NewProviderInitHandler),
                                       ('/admin/provider/solicit', admin.NewProviderSolicitHandler),
                                       ('/admin', admin.AdminIndexHandler),
                                       ('/admin/bookings', admin.AdminBookingsHandler),
                                       ('/admin/providers', admin.AdminProvidersHandler),
                                       # auth
                                       ('/login', auth_handler.LoginHandler),
                                       #('/create', auth_handler.CreateUserHandler),
                                        #RedirectRoute('/login/', auth_handler.LoginHandler, name='login', strict_slash=True),
                                        RedirectRoute('/logout/', auth_handler.LogoutHandler, name='logout', strict_slash=True),
                                      ], debug=True,
                                      config=webapp2_config)

