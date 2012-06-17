# -*- coding: utf-8 -*-

from base import BaseTest
from datetime import datetime, timedelta
import unittest
import testutil, util
from data import db
from data.model import Patient, Booking, User


class BookingTest(BaseTest):
    
    def test_booking_single_timeslot_available(self):
        ''' Create a booking in the available timeslot '''
        self.create_complete_provider_profile()
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # try to book monday 8am
        response = self.book_appointment(util.CAT_OSTEO, testutil.next_monday_date_string(), 8)
        # verify provider name
        response.mustcontain("Mr. Fantastic F.")
        # verify location
        response.mustcontain("at their clinic at 123 Main St. in Westmount")
        # verify date and time
        response.mustcontain("8:00")
        # verify bio and quote
        response.mustcontain("The quick brown fox jumped over the lazy dog")
        response.mustcontain("Areas of interest include treatment and management of spinal conditions with an emphasis on manual therapy and rehabilitative exercise.")
        
        
    def test_booking_single_timeslot_book_unavailable_time(self):
        ''' Create a booking in a timeslot with no availability '''
        self.create_complete_provider_profile()
        # Out Schedule is open only on Monday, try to book Tuesday
        response = self.book_appointment(util.CAT_OSTEO, testutil.next_weekday_date_string(testutil.TUESDAY), 14)
        # verify error messages
        response.mustcontain("Malheureusement, il n'y a pas de professionnels disponibles qui répondent à vos besoins")


    def test_booking_twice_in_same_timeslot(self):
        ''' Create a booking in the timeslot after another booking is made in the same timeslot 
            shows next available timeslot?
        '''

        self.create_complete_provider_profile()
        self.logout_provider()
        
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # go back to the main page and try to book monday 8am
        response = self.book_appointment(util.CAT_OSTEO, testutil.next_weekday_date_string(testutil.MONDAY), 8)

        # verify provider name
        response.mustcontain("Mr. Fantastic F.")
        # verify location
        response.mustcontain("at their clinic at 123 Main St. in Westmount")
        # verify date and time
        response.mustcontain("8:00")
                
        # email form
        email_form = response.forms[0]
        email_form['email'] = 'pat@patient.com'
        new_patient_response = email_form.submit()
        
        # profile form
        new_patient_response.mustcontain('Nouveau Patient')
        patient_form = new_patient_response.forms[0]
        patient_form['first_name'] = first_name = 'Pat!'
        patient_form['last_name'] = 'Patient'
        patient_form['telephone'] = '514-123-1234'
        patient_form['terms_agreement'] = '1'
        booking_confirm_page = patient_form.submit()
        
        # check confirm page
        booking_confirm_page.mustcontain("An email was sent with your appointment details and a confirmation code.")
        booking_confirm_page.mustcontain("Please check your inbox and click on the link to finish the process.")
        
        
        ## COMPLETE BOOKING (email and all that)
        
        # check email
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]

        patient = Patient.query(Patient.email == self._TEST_PATIENT_EMAIL).get()
        booking = Booking.query(Booking.patient == patient.key).get()
        provider = booking.provider.get()
        
        self.assertEqual(m.subject, 'veosan reservation - %s' % 'Ostéopathe')
        
        # assert that activation link is in the email body
        user = User.query(User.key == patient.user).get()
        self.assertTrue('http://localhost/user/activation/%s' % user.signup_token in m.body.payload)
 
        # click link in email
        activation_response = self.testapp.get('/user/activation/%s' % str(user.signup_token))
        
        # choose a password
        activation_response.mustcontain('Choisissez votre mot de passe')
        activation_response_form = activation_response.forms[0]
        activation_response_form['password'] = self._TEST_PATIENT_PASSWORD
        activation_response_form['password_confirm'] = self._TEST_PATIENT_PASSWORD
        booking_confirm_page = activation_response_form.submit()
        
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you %s!' % patient.first_name)
        # content check
        
        
        # now try to book again
        # go back to the main page and try to book monday 8am again
        response = self.book_appointment(util.CAT_OSTEO, testutil.next_weekday_date_string(testutil.MONDAY), 8)

        # get the next slot
        response.mustcontain("9:00")
        response.mustcontain("Mr. Fantastic F.")
        response.mustcontain("at their clinic at 123 Main St. in Westmount")

        
    def test_booking_new_patient(self):
        ''' Create a booking in the available timeslot '''
        
        # setup a provider
        self.create_complete_provider_profile()
        self.logout_provider()
        # at this point there is one fully completed profile with a single timeslot available (Monday 8-13)
        # go back to the main page and try to book monday 8am
        response = self.book_appointment(util.CAT_OSTEO, testutil.next_weekday_date_string(testutil.MONDAY), 8)

        # email form
        email_form = response.forms[0]
        email_form['email'] = 'pat@patient.com'
        new_patient_response = email_form.submit()
        
        new_patient_response.mustcontain('Nouveau Patient')
        patient_form = new_patient_response.forms[0]
        patient_form['first_name'] = first_name = 'Pat!'
        patient_form['last_name'] = 'Patient'
        patient_form['telephone'] = '514-123-1234'
        patient_form['terms_agreement'] = '1'
        booking_confirm_page = patient_form.submit()
        
        # check confirm page
        booking_confirm_page.mustcontain("An email was sent with your appointment details and a confirmation code.")
        booking_confirm_page.mustcontain("Please check your inbox and click on the link to finish the process.")
        
        # check email
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        self.assertEqual(1, len(messages))
        m = messages[0]
        
        patient = Patient.query(Patient.email == self._TEST_PATIENT_EMAIL).get()
        booking = Booking.query(Booking.patient == patient.key).get()
        provider = booking.provider.get()
        
        #category_label = dict(util.getAllCategories())[provider.category]

        self.assertEqual(m.subject, 'veosan reservation - %s' % 'Ostéopathe')
        
        # assert that activation link is in the email body
        user = User.query(User.key == patient.user).get()
        self.assertTrue('http://localhost/user/activation/%s' % user.signup_token in m.body.payload)
 
        # click link in email
        activation_response = self.testapp.get('/user/activation/%s' % str(user.signup_token))
        
        # choose a password
        activation_response.mustcontain('Choisissez votre mot de passe')
        activation_response_form = activation_response.forms[0]
        activation_response_form['password'] = self._TEST_PATIENT_PASSWORD
        activation_response_form['password_confirm'] = self._TEST_PATIENT_PASSWORD
        booking_confirm_page = activation_response_form.submit()

        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you %s!' % first_name)
        # content check
         
    def test_booking_existing_patient(self):
        self.test_booking_new_patient()
        self.logout_patient()
        # Try making another booking as Pat the patient
        today = datetime.today()
        next_monday = today + timedelta(days=-today.weekday(), weeks=1)
        next_monday_string = datetime.strftime(next_monday, "%Y-%m-%d")
        # We already have an appointment at 8AM, let's now book 10AM
        result_response = self.book_appointment('osteopath', next_monday_string, '10')
        # email form
        email_form = result_response.forms[0]
        email_form['email'] = self._TEST_PATIENT_EMAIL
        # We are an existing patient, but not logged in, this should take us to the login page
        login_page = email_form.submit()
        login_page.mustcontain('Connexion à veosan')
        login_page.mustcontain('booking_key')
        # email should be set in form
        login_page.mustcontain(self._TEST_PATIENT_EMAIL)
        login_form = login_page.forms[0]
        login_form['password'] = self._TEST_PATIENT_PASSWORD
        login_redirect = login_form.submit()
        booking_confirm_page = login_redirect.follow()
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you Pat!')
        
    def test_booking_with_loggedin_patient(self):
        self.test_booking_new_patient()
        self.logout_patient()
        # Try to login and book another appintment as Pat the patient
        self.login_as_patient()
        # book appointment
        today = datetime.today()
        next_monday = today + timedelta(days=-today.weekday(), weeks=1)
        next_monday_string = datetime.strftime(next_monday, "%Y-%m-%d")
        # We already have an appointment at 8AM, let's now book 10AM
        result_response = self.book_appointment('osteopath', next_monday_string, '10')
        # email form
        book_form = result_response.forms[0]
        # no email on form (can we assert this?)
        booking_confirm_page = book_form.submit()
        # patient email in navbar
        booking_confirm_page.mustcontain(self._TEST_PATIENT_EMAIL)
        # Title check
        booking_confirm_page.mustcontain('Thank you Pat!')
     
     
    def test_booking_fail_with_provider_without_terms_agreement(self):
        ''' Create a booking in the timeslot after another booking is made in the same timeslot '''
        
        self.create_complete_provider_profile()
        provider = db.get_provider_from_email(self._TEST_PROVIDER_EMAIL)
        provider.terms_agreement = False
        provider.terms_date = None
        provider.put()
        # book appointment
        response = self.book_appointment('osteopath', testutil.next_monday_date_string(), '8')
        response.mustcontain('Malheureusement')
        
        
           
        
if __name__ == "__main__":
    unittest.main()
    
    
