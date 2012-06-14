# -*- coding: utf-8 -*-

import logging, urlparse
import data.db as db
from data import db_search
import mail
from forms.base import BookingForm, EmailOnlyBookingForm
from forms.patient import PatientForm
from forms.user import LoginForm
from handler.base import BaseHandler
from handler.auth import patient_required
from datetime import datetime
import util
from utilities import time

class BaseBookingHandler(BaseHandler):
    '''Common functions for all booking handlers'''
    
    @staticmethod
    def render_confirmed_patient(handler, patient, **kw):
        # find the patient's bookings
        # TODO: does this work for multiple appointments? probably not
        booking = db.get_bookings_for_patient(patient)
        
        extra = {'patient': patient, 'booking': booking, 'provider': booking.provider.get()}
        kw.update(extra)
        handler.render_template('patient/confirm_appointment.html', **kw)
        
    def render_confirmed_booking(self, booking, **kw):        
        extra = {'patient': booking.patient.get(), 'booking': booking, 'provider': booking.provider.get()}
        kw.update(extra)
        self.render_template('patient/confirm_appointment.html', **kw)

    def search_and_render_results(self, booking, email_form=None):
        logging.info("Searching for providers for booking %s" % booking)
        booking_responses = db_search.provider_search(booking)
        if booking_responses:
            index = int(self.request.get('index', 0))
            self.render_result(booking, booking_responses, index, email_form)
        else:
            logging.warn('No provider found for booking: %s' % booking.key.urlsafe())
            emailForm = EmailOnlyBookingForm()
            self.renderFullyBooked(booking, emailForm) 
    
    def render_result(self, booking, booking_responses, index, email_form=None):
        br = booking_responses[index]
        # create email form if not passed (email_form is passed in when validation fails)
        if not email_form:
            email_form = EmailOnlyBookingForm()
        logging.info("Rendering result: active provider is %s at index %s: " % (br.provider.fullName(), index))
        kw = {'patient': None, 'booking': booking, 'booking_responses': booking_responses, 'index': index, 'form': email_form }
        self.render_template('search/result_caroussel.html', **kw)     
    
    def render_new_patient_form(self, patientForm, booking, user=None, **kw):
        extra = {'form': patientForm, 'booking': booking, 'provider': booking.provider.get(), 'user': user}
        kw.update(extra)
        self.render_template('patient/profile.html', **kw)
    
    def render_confirmation_email_sent(self, booking):
        kw = {'patient': booking.patient.get(), 'booking': booking, 'provider': booking.provider.get()}
        self.render_template('patient/confirmation_email_sent.html', **kw)

    def renderFullyBooked(self, booking, emailForm=None, **kw):
        self.render_template('search/no_result.html', booking=booking, form=emailForm, **kw) 
        
    def create_booking_form(self, payload):
        bookingform = BookingForm(payload)
        # set choices at run time because can't find a way to do lazy date and time localization in form declaration
        bookingform.category.choices = util.getAllCategories()
        bookingform.location.choices = util.getAllRegions()
        bookingform.booking_date.choices = time.getDatesList()
        bookingform.booking_time.choices = time.getTimesList()
        return bookingform
    
    
class IndexHandler(BaseBookingHandler):
    def get(self):
        bookingform = self.create_booking_form(self.request.GET)
        self.render_template('index.html', form=bookingform)
        
    def post(self):
        ''' Renders 2nd page: Result + Confirm button
        TODO: Replace with passing booking properties and provider key, saving only after the patient logging ??? 
        '''
        bookingform = self.create_booking_form(self.request.POST)
        if bookingform.validate():
            booking = db.storeBooking(self.request.POST, None, None)
            logging.debug('Created booking: %s' % booking)
            self.search_and_render_results(booking)
        else:
            self.render_template('index.html', form=bookingform)

                
class SearchNextHandler(BaseBookingHandler):
    '''
        Handler to travel through the search results
    '''
    def post(self):
        # get request info
        index = int(self.request.get('index'))
        booking_key = self.request.get('bk')
        booking = db.get_from_urlsafe_key(booking_key)
        booking_responses = db_search.provider_search(booking)
        if booking_responses:
            self.render_result(booking, booking_responses, index)
        else:
            logging.warn('No provider found for booking: %s' % booking.key.urlsafe())
            emailForm = EmailOnlyBookingForm()
            self.renderFullyBooked(booking, emailForm)
            

class PatientBookHandler(BaseBookingHandler):
    
    @patient_required
    def get(self):
        '''
            Displays booking confirmation.
            Protected by @patient_required so that only logged in patient can see their own booking confirm
        '''
        booking_key = self.request.get('bk')
        logging.info('(PatientBookHandler.get) Showing Booking confirmation for %s' % booking_key)
        booking = db.get_from_urlsafe_key(booking_key)
        self.render_confirmed_booking(booking) 
        
       
    def post(self):
        '''
            1. Save selected provider and timeslot to the booking
            2. Add the patient using the User
        '''
        booking = db.get_from_urlsafe_key(self.request.get('bk')) 
        # 1. Save provider and datetime in booking
        provider = db.get_from_urlsafe_key(self.request.get('provider_key')) 
        booking.provider = provider.key
        booking_datetime = datetime.strptime(self.request.get('booking_datetime'), '%Y-%m-%d %H:%M:%S')
        booking.request_datetime = booking_datetime
        booking.put()
        # 2. Add patient information
        email_form = EmailOnlyBookingForm(self.request.POST)
        user = self.get_current_user()
        if user:
            # form was only a submit button, we get the email from the user logged in
            email = user.get_email()
            # A user is logged in let's see if he is a patient (he might be a provider)
            patient = db.get_patient_from_user(user)
            if patient:
                # Patient is logged in
                logging.info('Patient %s is already logged in, confirming booking.' % email)
                booking.patient = patient.key
                booking.put()
                
                # skip activation stuff, send confirm email
                mail.email_booking_to_patient(self.jinja2, booking)
                
                self.render_confirmed_patient(self, patient) 
            else:
                # TODO ... If it's logged in and not a patient, it has to be a provider! Can they be both?    
                pass
            
        else:
            # Form has an email field, let's validate
            if email_form.validate():
                # store email in booking as requestEmail
                email = self.request.get('email')
                booking.request_email = email
                booking.put()
                existing_user = self.auth.store.user_model.get_by_auth_id(email)
                if existing_user:
                    existing_patient = db.get_patient_from_user(existing_user)
                    if existing_patient:
                        # email is in datastore, but not logged in
                        # link booking to patient and then check if same patient logs in (check is in @patient_required)
                        booking.patient = existing_patient.key
                        booking.put()
                        # send to login page with booking.key set
                        login_form = LoginForm()
                        login_form.email.data = email
                        self.render_template('login.html', form=login_form, booking=booking)
                    
                    else:
                        # user exists, not no patient profile attached (might be a provider)
                        
                        # 1. login, 2. patient profile, 3. confirm
                        pass
                        
                else:    
                    # email is not known, create new patient profile
                    logging.info('Patient does not exist for %s, creating new patient.' % email)
                    patientForm = PatientForm(self.request.POST)
                    # set email in form 
                    patientForm.email.data = email
                    self.render_new_patient_form(patientForm, booking)             
            else:
                # email validation failed. Show same results again
                self.search_and_render_results(booking, email_form)
            
            
class FullyBookedHandler(BaseBookingHandler):
    def get(self):
        logging.warn('FullyBooked GET Handler Not Implemented')
        pass
        
    def post(self):
        emailForm = EmailOnlyBookingForm(self.request.POST)
        booking = db.get_from_urlsafe_key(self.request.get('bk'))
        if emailForm.validate():
            ''' Stores email for Booking with No Result'''
            booking.requestEmail = self.request.get('email')
            booking.put()
            self.renderFullyBooked(booking)
        else:
            self.renderFullyBooked(booking, emailForm)
            


class NewPatientHandler(BaseBookingHandler):
    '''
        Handler for New Patient Form
    '''
    def post(self):
        # create patient form for validation
        patient_form = PatientForm(self.request.POST)
        # fetch booking from bk
        booking = db.get_from_urlsafe_key(self.request.get('bk'))
        # validate form
        if patient_form.validate():
            # create a patient from the form
            patient = db.store_patient(self.request.POST)
            
            # Create an empty user in Auth system
            user = self.create_empty_user_for_patient(patient)
            
            # create a signup token for new user
            token = self.create_signup_token(user)

            # activation url
            url_obj = urlparse.urlparse(self.request.url)
            activation_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/user/activation/' + token, '', '', ''))
            logging.info('(NewPatientHandler.post) generated activation url for user %s : %s ' %  (patient.email, activation_url))

            if user:
                # store booking
                booking.patient = patient.key
                booking.confirmed = user.confirmed = False
                booking.put()
                
                # booking succesful, send profile confirmation email
                mail.email_booking_to_patient(self.jinja2, booking, activation_url)
                
                self.render_confirmation_email_sent(booking)
            else:
                logging.error('User not created.')
                # TODO add custom validation to tell user that email is already in use.
                self.render_new_patient_form(patient_form, booking, error_message='Email already in use. Try to login instead.')

        else:   
            # validation failed        
            self.render_new_patient_form(patient_form, booking)
            
