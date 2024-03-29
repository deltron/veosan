from data import db
import logging
from forms.booking import AppointmentDetailsForLoggedInUser,\
    RegistrationDetailsForNewPatient, AppointmentDetails
from data.model import Booking, Patient
from webapp2_extras.i18n import to_utc
from datetime import datetime
from handler.patient import PatientBaseHandler
from handler.booking_pkg.booking_base_handler import BookingBaseHandler
from handler import auth
import mail
import json
from webapp2_extras import security
import urlparse
from google.appengine.ext import ndb


class BookFromPublicProfileDetails(BookingBaseHandler):
    def get(self, vanity_url=None, book_date=None, book_hour=None, book_minutes=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        booking_datetime_string = "%s %s:%s" % (book_date, book_hour, book_minutes)
        booking_datetime_utc = to_utc(datetime.strptime(booking_datetime_string, '%Y-%m-%d %H:%M'))
        if not provider.is_available(booking_datetime_utc):
            logging.warn("Trying to book a time not available in the schedule...")
            self.redirect("/" + vanity_url + "/book")
        else:
            booking_form = None
            
            user = self.get_current_user()
            if user:
                booking_form = AppointmentDetailsForLoggedInUser().get_form(provider=provider)
            else:
                # no user logged in, ask for email and stuff
                booking_form = AppointmentDetails().get_form(provider=provider)

            booking_form['booking_date'].data = book_date
            booking_form['booking_time'].data = book_hour + ":" + book_minutes
            
            self.render_template('provider/public/booking_details.html', provider=provider, booking_form=booking_form)
        
    
    def post(self, vanity_url=None):
        '''
            Booking process from public profile
        '''
        appointment_details_form = None
        provider = db.get_provider_from_vanity_url(vanity_url)
    
        user = self.get_current_user()
        if user:
            appointment_details_form = AppointmentDetailsForLoggedInUser().get_form(self.request.POST, provider=provider)
        else:
            appointment_details_form = AppointmentDetails().get_form(self.request.POST, provider=provider)
        
        provider = db.get_provider_from_vanity_url(vanity_url)
        if appointment_details_form.validate():
            # create the booking object
            booking = Booking()
            booking.provider = provider.key
            booking.booking_source = 'profile'
            
            booking_date = appointment_details_form['booking_date'].data
            booking_time = appointment_details_form['booking_time'].data
            booking.datetime = to_utc(datetime.strptime(booking_date + " " + booking_time, '%Y-%m-%d %H:%M'))
            booking.comments = appointment_details_form['comments'].data

            schedule = db.get_schedule_for_date_time(provider, booking_date, booking_time)
            booking.schedule = schedule.key            
            
            if appointment_details_form.__contains__('service'):
                service_key_from_form = appointment_details_form['service'].data
                if service_key_from_form:
                    service_key = ndb.Key(urlsafe=service_key_from_form)
                    provider_service = service_key.get()
                    if provider_service:
                        booking.service = service_key

            if user:
                # user is logged in, is this a patient?
                existing_patient = db.get_patient_from_user(user)
                if existing_patient:
                    booking.patient = existing_patient.key
                else:
                    self.link_user_to_new_patient(appointment_details_form, user, booking)
                    
                # confirm the booking since it is a "known" user
                booking.confirmed = True
                booking.email_sent_to_patient = False
                booking.email_sent_to_provider = False
                
                # save booking
                booking.put()
                
                # already logged in so go directly to bookings list
                self.redirect('/patient/bookings/' + booking.patient.urlsafe())
                
                # mail it to the patient
                mail.email_booking_to_patient(self, booking)
                
                # mail it to the provider
                mail.email_booking_to_provider(self, booking)
                    
            else:
                # no user is logged in, check if the email address exists, this means they just didn't log in
                email = appointment_details_form['email'].data

                existing_user = db.get_user_from_email(email)
                if existing_user:
                    existing_patient = db.get_patient_from_user(existing_user)
                    if existing_patient:                        
                        # email is in datastore, but not logged in
                        # link booking to existing patient 
                        booking.patient = existing_patient.key
                        booking.put()
                    else:
                        self.link_user_to_new_patient(appointment_details_form, user, booking)       
                    
                    # confirm the booking since it is a "known" user
                    booking.confirmed = True
                    booking.email_sent_to_patient = False
                    booking.email_sent_to_provider = False
                    
                    # save booking
                    booking.put()

                    # get the user to login
                    key = booking.key.urlsafe()
                    self.redirect('/login/booking/' + key)
                else:
                    # no patient, no user. get them to fill a profile in the form
                    booking.put()
                    
                    patient_form = RegistrationDetailsForNewPatient().get_form()
                    patient_form['terms_agreement'].data = True
                    patient_form['booking_date'].data = booking_date
                    patient_form['booking_time'].data = booking_time
                    patient_form['booking_key'].data = booking.key.urlsafe()
                    patient_form['email'].data = email

                    self.render_template('provider/public/booking_new_patient.html', provider=provider, patient_form=patient_form)
                        
            logging.info('Created booking from public profile: %s' % booking)
            
        else:
            self.render_template('provider/public/booking_details.html', provider=provider, booking_form=appointment_details_form)

    def link_user_to_new_patient(self, appointment_details_form, user, booking):
        # user but no patient
        # create a patient and link it to existing user
        patient = Patient() 
        
        # set the properties (just email)
        appointment_details_form.populate_obj(patient)
        self.set_gae_geography_from_headers(patient)
        
        # link to logged in user
        patient.user = user.key
        patient.email = user.get_email()
        
        # if it's a provider, copy over details like name, etc.
        provider = db.get_provider_from_user(user)
        if provider:
            patient.first_name = provider.first_name
            patient.last_name = provider.last_name        
        
        patient.put()
        
        booking.patient = patient.key
        booking.put()
        
        # add patient role to user
        user.roles.append(auth.PATIENT_ROLE)
        user.put()

 
 
 
class BookFromPublicProfileNewPatient(BookingBaseHandler):
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        patient_form = RegistrationDetailsForNewPatient().get_form(self.request.POST)
        
        if patient_form.validate():
            booking_key_urlsafe = patient_form['booking_key'].data
            booking = db.get_from_urlsafe_key(booking_key_urlsafe)

            # create a new patient
            patient = Patient()
                    
            patient_form.populate_obj(patient)
            self.set_gae_geography_from_headers(patient)
            patient.put()

            # create a new user
            user = self.create_empty_user_for_patient(patient)
            user.language = self.get_language()

            # set the password            
            password = patient_form['password'].data
            password_hash = security.generate_password_hash(password, length=12)    
            user.password = password_hash
            user.put()
            
            # login with new password
            self.login_user(user.get_email(), password)

            # store booking
            user = patient.user.get()
            booking.patient = patient.key
            booking.confirmed = user.confirmed = False
            booking.put()

            # send a confirmation/activation email
            url_obj = urlparse.urlparse(self.request.url)
            activation_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/login/booking/' + booking.key.urlsafe(), '', '', ''))
            logging.info('(NewPatientHandler.post) generated activation url for user %s : %s ' %  (patient.email, activation_url))
            mail.email_booking_to_patient(self, booking, activation_url)
            
            PatientBaseHandler.render_confirmation_email_sent(self, booking)
        else:
            self.render_template('provider/public/booking_new_patient.html', provider=provider, patient_form=patient_form)

                