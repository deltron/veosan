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

class PatientLookup(BookingBaseHandler):
    def post(self):
        email = self.request.get('email')
        if email:
            patient = db.get_patient_from_email(email)
            if patient:
                data = { 'first_name' : patient.first_name, 
                         'last_name' : patient.last_name,
                         'telephone' : patient.telephone }
                
                return_string = json.dumps(data)
                self.response.write(return_string)



class BookFromPublicProfileRegistration(BookingBaseHandler):
    def get(self, vanity_url=None, book_date=None, book_time=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        if not provider.is_available(book_date, book_time):
            logging.warn("Trying to book a time not available in the schedule...")
            self.redirect("/" + vanity_url + "/book")
        else:
            form = None
            
            user = self.get_current_user()
            if user:
                # user is logged in, don't ask for name and email
                patient_from_user = db.get_patient_from_user(user)
                provider_from_user = db.get_provider_from_user(user)

                if patient_from_user or provider_from_user:
                    form = AppointmentDetailsForLoggedInUser().get_form()
                else:
                    # logged in user is not a provider nor a patient
                    logging.error('Current logged in user has no provider or patient profile')    
            else:
                # no user logged in, ask for email and stuff
                form = AppointmentDetails().get_form()

            form['booking_date'].data = book_date
            form['booking_time'].data = book_time
            
            self.render_template('provider/public/booking_registration.html', provider=provider, email_details_form=form)
        
    
    def post(self, vanity_url=None):
        '''
            Booking process from public profile
        '''
        appointment_details_form = None
    
        user = self.get_current_user()
        if user:
            appointment_details_form = AppointmentDetailsForLoggedInUser().get_form(self.request.POST)
        else:
            appointment_details_form = AppointmentDetails().get_form(self.request.POST)
        
        provider = db.get_provider_from_vanity_url(vanity_url)
        if appointment_details_form.validate():
            # create the booking object
            booking = Booking()
            booking.provider = provider.key
            booking.booking_source = 'profile'
            
            booking_date = self.request.get('booking_date')
            booking_time = self.request.get('booking_time')
            booking.datetime = to_utc(datetime.strptime(booking_date + " " + booking_time, '%Y-%m-%d %H'))
            booking.comments = self.request.get('comments')

            schedule = db.get_schedule_for_date_time(provider, booking_date, booking_time)
            booking.schedule = schedule.key            

            if user:
                # user is logged in, is this a patient?
                existing_patient = db.get_patient_from_user(user)
                if existing_patient:
                    booking.patient = existing_patient.key
                else:
                    # user but no patient (probably a provider)
                    # create a patient and link it to existing user
                    patient = Patient()
                    
                    # set the properties (just email)
                    appointment_details_form.populate_obj(patient)
    
                    self.set_gae_geography_from_headers(patient)
                    
                    # link to logged in user
                    patient.user = user.key
                    patient.email = user.get_email()
                    patient.put()
                    
                    booking.patient = patient.key
                    
                    # add patient role to user
                    user.roles.append(auth.PATIENT_ROLE)
                                
                    user.put()
                    
                # confirm the booking since it is a "known" user
                booking.confirmed = True
                
                # save booking
                booking.put()
                              
                self.redirect('/patient/bookings')
                
                # mail it to the patient
                mail.email_booking_to_patient(self, booking)
                
                # mail it to the provider
                mail.email_booking_to_provider(self, booking)
                    
            else:
                # no user is logged in, check if the email address exists, this means they just didn't log in
                email = appointment_details_form['email'].data

                existing_user = db.get_user_from_email(email)
                if existing_user:
                    logging.info('Email is existing user %s' % email)
                    existing_patient = db.get_patient_from_user(existing_user)
                    if existing_patient:
                        logging.info('Email is existing patient %s' % email)
                        
                        # email is in datastore, but not logged in
                        # link booking to patient and then check if same patient logs in (check is in @patient_required)
                        booking.patient = existing_patient.key
                        booking.put()
                        
                        # get the user to login
                        key = booking.key.urlsafe()
                        self.redirect('/login/booking/' + key)
                        
                else:
                    # no patient, get them to fill a profile in the form
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
            self.render_template('provider/public/booking_registration.html', provider=provider, appointment_details_form=appointment_details_form)
 
 
 
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
            
            # send a confirmation/activation email
            PatientBaseHandler.link_patient_and_send_confirmation_email(self, booking, patient)
            
        else:
            self.render_template('provider/public/booking_new_patient.html', provider=provider, patient_form=patient_form)

                