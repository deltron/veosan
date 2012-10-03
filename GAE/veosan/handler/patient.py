# -*- coding: utf-8 -*-

import logging, urlparse
import data.db as db
import mail
from handler.base import BaseHandler
from operator import attrgetter
from handler import auth

class PatientBaseHandler(BaseHandler):
    '''Common functions for all patient handlers'''
        
    @staticmethod
    def render_bookings(handler, patient, provider=None, **kw):
        ''' Render a patient's bookings '''
        bookings = db.get_bookings_for_patient(patient)
        bookings = sorted(bookings, key=attrgetter('datetime'), reverse=True)
        handler.render_template('patient/booking_list.html', provider=provider, bookings=bookings, **kw)
    
    @staticmethod
    def render_confirmation_email_sent(handler, booking):
        kw = {'patient': booking.patient.get(), 'booking': booking, 'provider': booking.provider.get()}
        handler.render_template('patient/confirmation_email_sent.html', **kw)
                
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
                if auth.PROVIDER_ROLE in user.roles:
                    provider = db.get_provider_from_user(user)
                    self.render_bookings(self, provider=provider, patient=patient)
                else:
                    self.render_bookings(self, patient=patient)
            else:
                logging.info("(ListPatientBookings) No patient associated to logged in user: %s" % user.get_email())
                self.redirect("/")
            
        else:
            logging.info("(ListPatientBookings) Trying to list bookings but no user logged in")
            self.redirect("/")


