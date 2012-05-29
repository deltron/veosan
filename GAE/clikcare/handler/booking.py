# -*- coding: utf-8 -*-

import logging
import data.db as db, mail
from forms.base import BookingForm, PatientForm, EmailOnlyBookingForm
from handler.base import BaseHandler


class BaseBookingHandler(BaseHandler):
    '''Common functions for all booking handlers'''
    
    def renderConfirmedBooking(self, booking, **extra):
        tv = {'patient': booking.patient.get(), 'booking': booking, 'provider': booking.provider.get()}
        tv.update(extra)
        self.render_template('patient/book.html', **tv)
        
    def renderNewPatientForm(self, patientForm, booking, **extra):
        tv = {'form': patientForm, 'booking': booking, 'provider': booking.provider.get()}
        tv.update(extra)
        self.render_template('patient/new.html', **tv)
        
    def renderFullyBooked(self, booking, emailForm=None, **extra):
        self.render_template('no_result.html', booking=booking, form=emailForm, **extra) 
        
        
    
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
            
            # TODO rework this:
            
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
                    booking.patient = patient.key
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
                    booking.patient = patient.key
                    booking.put()
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