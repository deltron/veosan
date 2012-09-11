from data import db
import logging
from forms.booking import AppointmentDetailsForLoggedInUser, AppointmentDetailsForNewPatient
from data.model import Booking, Patient
from webapp2_extras.i18n import to_utc
from datetime import datetime
from forms.user import LoginForm
from handler.patient import PatientBaseHandler
from handler.booking_pkg.booking_base_handler import BookingBaseHandler
from handler import auth
import mail


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
                form = AppointmentDetailsForNewPatient().get_form()
                form['terms_agreement'].data = True

            form['booking_date'].data = book_date
            form['booking_time'].data = book_time
            
            self.render_template('provider/public/booking_registration.html', provider=provider, email_details_form=form)
        
    
    def post(self, vanity_url=None):
        '''
            Booking process from public profile
        '''
        email_details_form = None
    
        user = self.get_current_user()
        if user:
            email_details_form = AppointmentDetailsForLoggedInUser().get_form(self.request.POST)
        else:
            email_details_form = AppointmentDetailsForNewPatient().get_form(self.request.POST)
        
        provider = db.get_provider_from_vanity_url(vanity_url)
        if email_details_form.validate():
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
                    
                    # set all the properties
                    email_details_form.populate_obj(patient)
                    
                    # set location info from request
                    if "X-AppEngine-Country" in self.request.headers:
                        patient.gae_country = self.request.headers["X-AppEngine-Country"]
                        
                    if "X-AppEngine-Region" in self.request.headers:
                        patient.gae_region = self.request.headers["X-AppEngine-Region"]
        
                    if "X-AppEngine-City" in self.request.headers:
                        patient.gae_city = self.request.headers["X-AppEngine-City"]
                    
                    if "X-AppEngine-CityLatLong" in self.request.headers:
                        patient.gae_city_lat_long = self.request.headers["X-AppEngine-CityLatLong"]

                    # link to logged in user
                    patient.user = user.key
                    patient.email = user.get_email()
                    patient.put()
                    
                    booking.patient = patient.key
                    
                    # add patient role to user
                    user.roles.append(auth.PATIENT_ROLE)
                    
                    # set user's default language
                    user.language = self.get_language()
            
                    user.put()
                    
                
                # confirm the booking since it is a "known" user
                booking.confirmed = True
                
                # save booking
                booking.put()
                
                # mail it to the provider
                mail.email_booking_to_provider(self, booking)
                
                self.redirect('/patient/bookings')
                    
            else:
                # no user is logged in, check if the email address exists, this means they just didn't log in
                email = email_details_form['email'].data

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
                        
                        # check if user is activated and has a password
                        if existing_user.is_activated_and_has_password():
                            # send to login page with booking.key set
                            key = booking.key.urlsafe()
                            self.redirect('/login/booking/' + key)

                        else:
                            # user exists but was never activated
                            logging.info('Patient exists but was not activated for %s, Skipping new patient form, but sending email to confirm.' % email)
                            PatientBaseHandler.link_patient_and_send_confirmation_email(self, booking, existing_patient)
                
                else:
                    # no user/patient, create one
                    patient = Patient()
                    
                    # set all the properties
                    email_details_form.populate_obj(patient)

                    # set location info from request
                    if "X-AppEngine-Country" in self.request.headers:
                        patient.gae_country = self.request.headers["X-AppEngine-Country"]
                        
                    if "X-AppEngine-Region" in self.request.headers:
                        patient.gae_region = self.request.headers["X-AppEngine-Region"]
        
                    if "X-AppEngine-City" in self.request.headers:
                        patient.gae_city = self.request.headers["X-AppEngine-City"]
                    
                    if "X-AppEngine-CityLatLong" in self.request.headers:
                        patient.gae_city_lat_long = self.request.headers["X-AppEngine-CityLatLong"]

                    user = self.create_empty_user_for_patient(patient)
                    
                    patient.put()
                    
                    booking.patient = patient.key
                    booking.put()
    
                    if user:
                        logging.info('New or non-activated user, sending confirmation email')
                        PatientBaseHandler.link_patient_and_send_confirmation_email(self, booking, patient)
                        
            logging.info('Created booking from public profile: %s' % booking)
            
        else:
            self.render_template('provider/public/booking_registration.html', provider=provider, email_details_form=email_details_form)
        
                