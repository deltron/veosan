# -*- coding: utf-8 -*-

import logging
import data.db as db
from data import db_search
import mail, util
from forms.booking import BookingForm, EmailOnlyBookingForm
from forms.patient import PatientForm
from forms.user import LoginForm
from handler.base import BaseHandler
from handler.auth import patient_required
from handler.patient import PatientBaseHandler
from datetime import datetime, date, timedelta
from utilities import time
from data.model import Booking
from webapp2_extras.i18n import to_utc

class BookingBaseHandler(BaseHandler):
    '''Common functions for all booking handlers'''
    
    @staticmethod
    def render_confirmed_patient(handler, patient, **kw):
        # find the patient's bookings
        # ASSUMPTION:
        # ==========
        # if the patient is being confirmed, they only have one appointment
        # so we take the first one from the restult list and display it
        booking = db.get_bookings_for_patient(patient)[0]
        
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
            # store results for analysis
            booking.search_results = map(lambda br: br.provider.key, booking_responses)
            booking.put()
            # render
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
        logging.info("Rendering result: active provider is %s at index %s: " % (br.provider.full_name(), index))
        kw = {'patient': None, 'booking': booking, 'booking_responses': booking_responses, 'index': index, 'form': email_form }
        self.render_template('search/result_carousel.html', **kw)     

    def renderFullyBooked(self, booking, emailForm=None, **kw):
        self.render_template('search/no_result.html', booking=booking, form=emailForm, **kw) 
    
    
class IndexHandler(BookingBaseHandler):
    def get(self):
        # for showing booking block
        booking_form = BookingForm().get_form(self.request.GET)
        self.render_template('index.html', form=booking_form)
        
    def post(self):        
        ''' Renders 2nd page: Result + Confirm button
        TODO: Replace with passing booking properties and provider key, saving only after the patient logging ??? 
        '''
        booking_form = BookingForm().get_form(self.request.POST)
        if booking_form.validate():
            booking = db.storeBooking(self.request.POST, None, None)
            
            logging.info('BOOKING %s' % booking)
            logging.debug('(IndexHandler) Created booking: %s' % booking)
            self.search_and_render_results(booking)
        else:
            logging.warn('Validation error in booking form %s' % booking_form.errors)
            self.render_template('index.html', form=booking_form, error_message=booking_form.errors)

                
class SearchNextHandler(BookingBaseHandler):
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
            

class BookingHandler(BookingBaseHandler):
    @patient_required
    def get(self):
        '''
            Displays booking confirmation.
            Protected by @patient_required so that only logged in patient can see their own booking confirm
        '''
        booking_key = self.request.get('bk')
        logging.info('(BookingHandler.get) Showing Booking confirmation for %s' % booking_key)
        booking = db.get_from_urlsafe_key(booking_key)
        self.render_confirmed_booking(booking) 
        
  
    def post(self):
        '''
            State: 
                - patient has chosen a provider and time slot
                - booking has been created and is referenced by 'bk' parameter
                
            1. Save selected provider and timeslot to the booking
            2. Add the patient using the User
        '''        
        logging.info('request %s' % self.request)

        booking = db.get_from_urlsafe_key(self.request.get('bk'))
        # 1. Save provider and datetime in booking
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        booking.provider = provider.key
        booking_datetime = to_utc(datetime.strptime(self.request.get('booking_datetime'), '%Y-%m-%d %H:%M:%S'))
        booking.datetime = booking_datetime
        booking.put()
        
        # is a user logged in? if so we can pull the information from their existin account
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
            # check if email was provided
            if self.request.get('email'):
                # no user is logged in, grab the email address from the booking form
                email_form = EmailOnlyBookingForm(self.request.POST)
                if email_form.validate():
                    # store email in booking as requestEmail
                    email = self.request.get('email')
                    
                    booking.request_email = email
                    booking.put()
                    
                    # check if the email address given is an existing user that hasn't logged in
                    # or a completely new user
                    existing_user = db.get_user_from_email(email)
                    if existing_user:
                        existing_patient = db.get_patient_from_user(existing_user)
                        if existing_patient:
                            # email is in datastore, but not logged in
                            # link booking to patient and then check if same patient logs in (check is in @patient_required)
                            booking.patient = existing_patient.key
                            booking.put()
                            # send to login page with booking.key set
                            login_form = LoginForm().get_form()
                            login_form.email.data = email
                            self.render_template('user/login.html', form=login_form, booking=booking)
                        
                        else:
                            # user exists, not no patient profile attached (might be a provider)
                            # 1. login, 2. patient profile, 3. confirm
                            logging.error("(BookingHandler) user exists, not no patient profile attached (might be a provider)")         
                    else:    
                        # email is not known, create new patient profile
                        logging.info('Patient does not exist for %s, creating new patient.' % email)
                        patient_form = PatientForm(self.request.POST)
                        PatientBaseHandler.render_new_patient_form(self, patient_form, booking)             
                else:
                    # email validation failed. Show same results again
                    self.search_and_render_results(booking, email_form)   
            else:    
                # no email provided, show new patient form with email field
                logging.info('Email not provided, creating new patient.')
                patient_form = PatientForm(self.request.POST)
                PatientBaseHandler.render_new_patient_form(self, patient_form, booking) 

            

class BookFromPublicProfile(BookingBaseHandler):
    '''
        Using vanity url, display schedule
    '''
    def get(self, vanity_url=None, start_date=None):
        # provoder already selection from public profile
        provider = db.get_provider_from_vanity_url(vanity_url)
        # 
        booking = Booking()
        booking.provider = provider.key
        booking.booking_source = 'profile'
        booking.put()
        logging.debug('Created booking from public profile: %s' % booking)
        
        if (not start_date) or (start_date <= date.today):
            start_date = time.tomorrow()
        period = timedelta(days=7)
        schedules = provider.get_schedules()
        datetimes_map = util.generate_datetimes_map(schedules, start_date, period)
        self.render_template('provider/booking_schedule.html', booking=booking, provider=provider, dtm=datetimes_map) 
        
             
                
class FullyBookedHandler(BookingBaseHandler):
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

