# -*- coding: utf-8 -*-

import logging, urlparse
import data.db as db
import mail
from forms.patient import PatientForm
from handler.base import BaseHandler
from operator import attrgetter

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
        ''' Render a patient's bookings '''
        bookings = db.get_bookings_for_patient(patient)
        bookings = sorted(bookings, key=attrgetter('datetime'), reverse=True)
        handler.render_template('patient/booking_list.html', bookings=bookings, **kw)
    
    @staticmethod
    def render_confirmation_email_sent(handler, booking):
        kw = {'patient': booking.patient.get(), 'booking': booking, 'provider': booking.provider.get()}
        handler.render_template('patient/confirmation_email_sent.html', **kw)
        
    @staticmethod
    def link_patient_and_send_confirmation_email(handler, booking, patient):
        # store booking
        user = patient.user.get()
        booking.patient = patient.key
        booking.confirmed = user.confirmed = False
        booking.put()
        # create a signup token for new user
        token = handler.create_signup_token(user)
        # activation url
        url_obj = urlparse.urlparse(handler.request.url)
        activation_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/user/activation/' + token, '', '', ''))
        logging.info('(NewPatientHandler.post) generated activation url for user %s : %s ' %  (patient.email, activation_url))
        mail.email_booking_to_patient(handler, booking, activation_url)
        PatientBaseHandler.render_confirmation_email_sent(handler, booking)
        
        
    @staticmethod
    def confirm_all_unconfirmed_bookings(patient):
        ubs = patient.get_future_unconfirmed_bookings()
        for booking in ubs:
            booking.confirmed = True
            booking.put()
            logging.info('booking confirmed %s' % booking)
        # simple name change for clarity
        confirmed_bookings = ubs
        return confirmed_bookings
        

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
        patient_form = PatientForm().get_form(self.request.POST)
        # fetch booking from bk
        booking = db.get_from_urlsafe_key(self.request.get('bk'))
        
        # validate form
        if patient_form.validate():
            # check if a patient already exists (double submit)
            patient = db.get_patient_from_email(patient_form['email'].data)
            if not patient:
                # create a patient from the form
                patient = db.store_patient(self.request.POST, patient_form)
                # Create an empty user in Auth system
                user = self.create_empty_user_for_patient(patient)
    
                if user:
                    logging.info('New or non-activated user, sending confirmation email')
                    PatientBaseHandler.link_patient_and_send_confirmation_email(self, booking, patient)
                else:
                    logging.error('User not created.')
                    # TODO add custom validation to tell user that email is already in use.
                    PatientBaseHandler.render_new_patient_form(patient_form, booking, error_message='Email already in use. Try to login instead.')
            else:
                # probably a double submit, just show the confirmation again
                PatientBaseHandler.render_confirmation_email_sent(handler=self, booking=booking)
                
        else:
            # validation failed        
            logging.error('New patient form validation failed')
            self.render_new_patient_form(self, patient_form, booking)
            

