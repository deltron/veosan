# -*- coding: utf-8 -*-

import logging, urlparse
import data.db as db
import mail
from forms.patient import PatientForm
from handler.base import BaseHandler

class PatientBaseHandler(BaseHandler):
    '''Common functions for all patient handlers'''
    
    @staticmethod
    def render_new_patient_form(handler, patient_form, booking, user=None, **kw):
        ''' 
            New patients are created from bookings. 
            The booking is saved in the database, get their email address from there
        '''
        
        extra = {'form': patient_form, 'booking': booking, 'provider': booking.provider.get(), 'user': user}
        kw.update(extra)
        handler.render_template('patient/profile.html', **kw)
    
    @staticmethod
    def render_bookings(handler, patient, **kw):
        bookings = db.get_bookings_for_patient(patient)
        handler.render_template('patient/booking_list.html', bookings=bookings, **kw)
    
    @staticmethod
    def render_confirmation_email_sent(handler, booking):
        kw = {'patient': booking.patient.get(), 'booking': booking, 'provider': booking.provider.get()}
        handler.render_template('patient/confirmation_email_sent.html', **kw)

class ListPatientBookings(PatientBaseHandler):
    def get(self):
        user = self.get_current_user()
        if user:
            patient = db.get_patient_from_user(user)
            if patient:
                self.render_bookings(self, patient)
            else:
                logging.info("(ListPatientBookings) No patient associated to logged in user: %s" % user.get_email())
                self.redirect("/")
            
        else:
            logging.info("(ListPatientBookings) Trying to list bookings but no user logged in")
            self.redirect("/")

class NewPatientHandler(PatientBaseHandler):
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
            
            # set the patient email from the booking object
            patient.email = booking.request_email
            
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
                
                self.render_confirmation_email_sent(self, booking)
            else:
                logging.error('User not created.')
                # TODO add custom validation to tell user that email is already in use.
                self.render_new_patient_form(patient_form, booking, error_message='Email already in use. Try to login instead.')

        else:   
            # validation failed        
            logging.error('New patient form validation failed')
            self.render_new_patient_form(self, patient_form, booking)
            
