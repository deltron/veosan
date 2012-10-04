# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
import testutil

class BookingTest(BaseTest):
    def test_booking_existing_patient(self):
        self.create_provider_and_enable_booking()
        # book once from public profile
        date_string = testutil.next_monday_date_string()
        time_string = '10'
        self.book_from_public_profile(date_string, time_string)
        self.patient_confirms_latest_booking(date_string, time_string, logged_in=True)
        self.logout_patient()
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        patient_email_count = len(messages)
        self.assertEqual(patient_email_count, 1)

        # book again from public profile        
        date_string = testutil.next_monday_date_string()
        time_string = '11'
        self.book_from_public_profile(date_string, time_string)
        
        # did we receive another email?
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PATIENT_EMAIL)
        patient_email_count = len(messages)
        self.assertEqual(patient_email_count, 2)

        provider_messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        provider_email_count = len(provider_messages)
        self.assertEqual(provider_email_count, 2)
        
    def test_book_from_public_profile_new_patient(self):
        self.create_provider_and_enable_booking()
        # Book from public profile
        date_string = testutil.next_monday_date_string()
        time_string = '10'
        self.book_from_public_profile(date_string, time_string)
        
        # provider should not see the booking yet, check provider bookings list, should be empty as booking is not confirmed
        self.login_as_provider()
        provider_bookings = self.testapp.get('/provider/bookings/' + self._TEST_PROVIDER_VANITY_URL)
        provider_bookings.mustcontain('Vous n’avez aucun rendez-vous prévu')
        # no email sent to provider (patient is not confirmed)
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(0, len(messages))
        self.logout_provider()
        
        # patient confirms
        self.patient_confirms_latest_booking(date_string, time_string)


    def test_public_profile_book_no_password_returning_patient(self):
        self.create_provider_and_enable_booking()
        # book once from public profile
        date_string = testutil.next_monday_date_string()
        time_string = '10'
        self.book_from_public_profile(date_string, time_string)
        
        # provider should not see the booking yet, check provider bookings list, should be empty as booking is not confirmed
        self.login_as_provider()
        provider_bookings = self.testapp.get('/provider/bookings/' + self._TEST_PROVIDER_VANITY_URL)
        provider_bookings.mustcontain('Vous n’avez aucun rendez-vous prévu')
        # no email sent to provider (patient is not confirmed)
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        self.assertEqual(0, len(messages))
        self.logout_provider()
        
        self.patient_confirms_latest_booking(date_string, time_string, new_user=False)
        
        # book second time from public profile
        date_string = testutil.next_monday_date_string()
        time_string = '11'
        self.book_from_public_profile(date_string, time_string)
        self.patient_confirms_latest_booking(date_string, time_string, new_user=False)
        


    def test_booking_inside_available_schedule(self):
        ''' if someone forces the URL to book something outside available schedule '''
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")

        # Monday 9-12 should be available, let's visit public profile and check
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Lundi")
        response.mustcontain("9:00")
        
        # try to book monday at 10h (which is available)
        next_monday = testutil.next_weekday_date_string(0)
        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book/' + next_monday + '/' + '10')
       
        # should not fail, should be registration page
        response.mustcontain(no="Choisissez la date et l'heure de votre rendez-vous")
        response.mustcontain(no="button"+next_monday)
        response.mustcontain("Nouveau rendez-vous")
        response.mustcontain("Votre rendez-vous")
        response.mustcontain(next_monday)


    def test_booking_outside_available_schedule(self):
        ''' if someone forces the URL to book something outside available schedule '''
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")

        # Monday 9-12 should be available, let's visit public profile and check
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Lundi")
        response.mustcontain("9:00")
        
        # try to book monday at 17h (which is not available)
        next_monday = testutil.next_weekday_date_string(0)
        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book/' + next_monday + '/' + '17')
       
        # should fail and redirect to booking page with list of available times
        response = response.follow()
        response.mustcontain("Choisissez la date et l'heure de votre rendez-vous")
        response.mustcontain("button-"+next_monday+"-9")

    def test_booking_inside_available_schedule_but_booked_by_someone_else(self):
        ''' if someone forces the URL to book something outside available schedule '''
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")

        self.logout_admin()
        
        # book an appointment for next monday at 10am
        next_monday = testutil.next_weekday_date_string(0)
        self.book_from_public_profile(next_monday, 10, self._TEST_PATIENT_EMAIL, self._TEST_PATIENT_TELEPHONE)
        
        self.patient_confirms_latest_booking(next_monday, 10, logged_in=True)
        
        self.logout_patient()
        
        # do it again with another patient (this should fail)
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book/' + next_monday + '/' + '17')
       
        # should fail and redirect to booking page with list of available times
        response = response.follow()
        response.mustcontain("Choisissez la date et l'heure de votre rendez-vous")
        response.mustcontain("button-"+next_monday)        
        

    
    # Test: double booking: one patient with 2 providers at same time

    def test_schedule_display(self):
        ''' Test that schedule is properly displayed '''
        # create provider and add schedules
        self.create_complete_provider_profile()
        self.login_as_provider()
        start_time=9
        self.provider_schedule_set_one_timeslot_action(day='monday', start_time=start_time, end_time=12)
        self.provider_schedule_set_one_timeslot_action(day='wednesday', start_time=start_time, end_time=12)
        self.logout_provider()
        
        # enable booking
        self.login_as_admin()
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")
        self.logout_admin()
        
        # check that all schedule time buttons are there.
        schedule_page = self.testapp.get('/%s/book' % self._TEST_PROVIDER_VANITY_URL)
        monday_date_string = testutil.next_weekday_date_string(0)
        schedule_page.mustcontain('button-%s-%s' % (monday_date_string, start_time))
        wed_date_string = testutil.next_weekday_date_string(2)
        schedule_page.mustcontain('button-%s-%s' % (wed_date_string, start_time))
        
         
    def test_navigate_schedule(self):
        # create and confirm booking
        self.test_book_from_public_profile_new_patient()
        
        # check that all schedule time buttons are there.
        schedule_page = self.testapp.get('/%s/book' % self._TEST_PROVIDER_VANITY_URL)
        next_week_page = schedule_page.click(linkid='next_week_button')
        
        
    def test_booking_removed_from_public_profile_availability(self):
        ''' if someone forces the URL to book something outside available schedule '''        
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")

        self.logout_admin()
        
        # check it appears as available on public profile and booking page
        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # book an appointment for next monday at 10am
        next_monday = testutil.next_weekday_date_string(0)
        self.book_from_public_profile(next_monday, 10, 
                                      self._TEST_PATIENT_EMAIL, self._TEST_PATIENT_TELEPHONE)
        
        self.patient_confirms_latest_booking(next_monday, 10, logged_in=True)
        
        self.logout_patient()
        
        # check schedule on public profile        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no=testutil.next_monday_date_string()+"/10")
        response.mustcontain(no="button-"+testutil.next_monday_date_string()+"-10")
        
        # check the book
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book')
        response.mustcontain(no=testutil.next_monday_date_string()+"/10")
        response.mustcontain(no="button-"+testutil.next_monday_date_string()+"-10")


    def test_booking_as_a_provider_logged_in(self):
        ''' Book an appointment as a provider '''
        self.create_complete_provider_profile()
        self.logout_provider()
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")
        self.logout_admin()
        
        # book an appointment for next monday at 10am with yourself (as returning patient, because already a user)
        self.login_as_provider()
        next_monday = testutil.next_weekday_date_string(0)
        # Book an appointment with yourself
        self.book_from_public_profile(next_monday, 10, self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_TELEPHONE)
        
        # check schedule on public profile        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no=testutil.next_monday_date_string()+"/10")
        response.mustcontain(no="button-"+testutil.next_monday_date_string()+"-10")
        
        # check the book
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book')
        response.mustcontain(no=testutil.next_monday_date_string()+"/10")
        response.mustcontain(no="button-"+testutil.next_monday_date_string()+"-10")
        
        # check emails
        messages = self.mail_stub.get_sent_messages(to=self._TEST_PROVIDER_EMAIL)
        provider_email_count = len(messages)
        
        # 2 - one for the patient side and one for the provider side
        self.assertEqual(provider_email_count, 2)
        for m in messages:
            self.assertEqual(self._TEST_PROVIDER_EMAIL, m.to)
            self.assertNotIn('None',  m.body.payload)
        
        
    def test_booking_second_appointment_as_a_patient_logged_in(self):
        ''' if someone forces the URL to book something outside available schedule '''        
        self.create_complete_provider_profile()
        self.logout_provider()
        
        self.login_as_admin()
        
        # enable booking
        response = self.testapp.get('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain("Show booking=True")

        self.logout_admin()
        
        # check it appears as available on public profile and booking page
        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # book an appointment for next monday at 10am
        next_monday = testutil.next_weekday_date_string(0)
        self.book_from_public_profile(next_monday, 10, 
                                      self._TEST_PATIENT_EMAIL, self._TEST_PATIENT_TELEPHONE)
        
        self.patient_confirms_latest_booking(next_monday, 10)
                
        # check schedule on public profile        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no=testutil.next_monday_date_string()+"/10")
        response.mustcontain(no="button-"+testutil.next_monday_date_string()+"-10")
        
        # check the book
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book')
        response.mustcontain(no=testutil.next_monday_date_string()+"/10")
        response.mustcontain(no="button-"+testutil.next_monday_date_string()+"-10")


        # book an appointment for next monday at 11am
        self.book_from_public_profile(next_monday, 11, 
                                      self._TEST_PATIENT_EMAIL, self._TEST_PATIENT_TELEPHONE)
        
        # logout patient
        self.logout_patient()
        
        # check schedule on public profile        
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        response.mustcontain(no=testutil.next_monday_date_string()+"/11")
        response.mustcontain(no="button-"+testutil.next_monday_date_string()+"-11")
        
        # check the book
        response = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL + '/book')
        response.mustcontain(no=testutil.next_monday_date_string()+"/11")
        response.mustcontain(no="button-"+testutil.next_monday_date_string()+"-11")
        
        # check provider receives emails for each appointment
        self.check_appointment_email_to_provider(next_monday, 10)
        self.check_appointment_email_to_provider(next_monday, 11)


if __name__ == "__main__":
    unittest.main()
    
    
