# -*- coding: utf-8 -*-

import logging
import data.db as db, mail
from forms.base import BookingForm, PatientForm, EmailOnlyBookingForm
from forms.login import LoginForm
from handler.base import BaseHandler
from handler.auth import patient_required
import util

class BaseBookingHandler(BaseHandler):
    '''Common functions for all booking handlers'''
    
    def renderConfirmedBooking(self, booking, **extra):
        tv = {'patient': booking.patient.get(), 'booking': booking, 'provider': booking.provider.get()}
        tv.update(extra)
        self.render_template('patient/book.html', **tv)
        
    def renderNewPatientForm(self, patientForm, booking, user=None, **extra):
        tv = {'form': patientForm, 'booking': booking, 'provider': booking.provider.get(), 'user': user}
        tv.update(extra)
        self.render_template('patient/new.html', **tv)
        
    def renderFullyBooked(self, booking, emailForm=None, **extra):
        self.render_template('booking/no_result.html', booking=booking, form=emailForm, **extra) 
        
    def create_booking_form(self, payload):
        bookingform = BookingForm(payload)
        # set choices at run time because can't find a way to do lazy date and time localization in form declaration
        bookingform.category.choices = util.getAllCategories()
        bookingform.location.choices = util.getAllRegions()
        bookingform.booking_date.choices = util.getDatesList()
        bookingform.booking_time.choices = util.getTimesList()
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
                self.render_template('booking/result.html', **tv) 
            else:
                logging.warn('No provider found for booking: %s' % booking.key.urlsafe())
                emailForm = EmailOnlyBookingForm()
                self.renderFullyBooked(booking, emailForm) 
        else:
            self.render_template('index.html', form=bookingform)


class PatientBookHandler(BaseBookingHandler):
    
    @patient_required
    def get(self):
        '''
            Displays booking confirmation.
            Protected by @patient_required so that only logged in patient can see their own booking confirm
        '''
        booking_key = self.request.get('bk')
        logging.info('Showing Booking confirmation for %s' % booking_key)
        booking = db.get_from_urlsafe_key(booking_key)
        self.renderConfirmedBooking(booking) 
        
        
    '''
        Handler to confirm the booking and create new patient record
    '''
    def post(self):
        'We have a booking with a provider, we need to add the patient using the User'
        booking = db.get_from_urlsafe_key(self.request.get('bk')) 
        email_form = EmailOnlyBookingForm(self.request.POST)
        user = self.get_current_user()
        if user:
            # form was only a submit button, we get the email from the user logged in
            email = user.get_email()
            # A user is logged in let's see if he is a patient (he might be a provider)
            patient = db.get_patient_profile(user)
            if patient:
                # Patient is logged in
                logging.info('Patient %s is already logged in, confirming booking.' % email)
                booking.patient = patient.key
                booking.put()
                self.renderConfirmedBooking(booking) 
            else:
                # user logged in, but not a patient, got to new patient form with the user.key set
                logging.info('User %s is logged in, but not a patient, creating new patient.' % email)
                patientForm = PatientForm(self.request.POST)
                self.renderNewPatientForm(patientForm, booking, user)   
            
        else:
            # Form has an email field, let's validate
            if email_form.validate():
                # store email in booking as requestEmail
                email = self.request.get('email')
                booking.request_email = email
                booking.put()
                existing_user = self.auth.store.user_model.get_by_auth_id(email)
                if existing_user:
                    existing_patient = db.get_patient_profile(existing_user)
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
                    self.renderNewPatientForm(patientForm, booking)             
            else:
                # email form validation failed
                tv = {'patient': None, 'booking': booking, 'p': booking.provider, 'form': email_form }
                self.render_template('booking/result.html', **tv) 
            
            
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
            


class PatientBookForNewHandler(BaseBookingHandler):
    '''
        Handler for New Patient Form
    '''
    def post(self):
        # create patient form for validation
        patientForm = PatientForm(self.request.POST)
        # fetch booking from bk
        booking = db.get_from_urlsafe_key(self.request.get('bk'))
        if patientForm.validate():
            # Create User in Auth system
            email = self.request.get('email')
            password = self.request.get('password')
            user = self.create_user(email, password)
            if user:
                # Store New Patient
                patient = db.storePatient(self.request.POST, user)
                if (patient):
                    # store booking
                    booking.patient = patient.key
                    booking.put()
                    # auto-loggin patient
                    self.login_user(email, password)
                    # booking succesfull, send email
                    mail.emailBookingToPatient(self.jinja2, booking)
                    self.renderConfirmedBooking(booking)
                else:
                    logging.error("No booking saved because patient is None")
                    self.renderNewPatientForm(patientForm, booking, error_message='Error while saving your booking. Please contact us.')
            else:
                logging.error('User not created.')
                # TODO add custom validation to tell user that email is already in use.
                self.renderNewPatientForm(patientForm, booking, error_message='Email already in use. Try to login instead.')
                
            
        else:           
            self.renderNewPatientForm(patientForm, booking)    