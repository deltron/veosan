# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderTest(BaseTest):
    
    def test_no_form_on_schedule_page(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)
        
        response.mustcontain(no="schedule_form")
        
        
    def test_add_time_to_schedule(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)
        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/9')
        schedule_form = response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 9
        schedule_form['end_time'] = 17
        response = schedule_form.submit()
        # check on the schedule admin page
        response.mustcontain('9h-17h')
        # check admin providers
        self.login_as_admin()
        admin_page = self.testapp.get('/admin/providers')
        admin_page.mustcontain('8')
        self.logout_admin()

    def test_delete_time_from_schedule(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)

        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/9')

        schedule_form = response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 9
        schedule_form['end_time'] = 17

        response = schedule_form.submit()
        
        # check on the schedule admin page
        response.mustcontain('9h-17h')

        # now find and delete it
        modal_response = response.click(linkid='tuesday_9_link')

        delete_response = modal_response.click(description=' Effacer ')
        
        delete_response.mustcontain(no='9h-17h')
    
    def test_change_time_in_schedule(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)

        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/9')

        schedule_form = response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 9
        schedule_form['end_time'] = 17

        response = schedule_form.submit()
        
        # check on the schedule page
        response.mustcontain('9h-17h')

        # now find and change it
        modal_response = response.click(linkid='tuesday_9_link')
        schedule_form = modal_response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 9
        schedule_form['end_time'] = 13
        
        response = schedule_form.submit()
        
        # check on the schedule page
        response.mustcontain('9h-13h')

    
    
    def test_end_time_before_start_time(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)

        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/9')

        schedule_form = response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 17
        schedule_form['end_time'] = 9
        
        response = schedule_form.submit()
        response.mustcontain("End time must be after start time")


    def test_click_plus_on_tuesday_10am(self):
        # verify modal is populated with correct info
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)

        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/10')
        
        response.mustcontain('<option selected value="10">10h</option>')
        response.mustcontain('<option selected value="14">14h</option>')
        response.mustcontain('<option selected value="tuesday">Mardi</option>')


    def test_merge_overlapping_times(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)

        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/9')

        schedule_form = response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 9
        schedule_form['end_time'] = 12

        response = schedule_form.submit()
        
        # check on the schedule page
        response.mustcontain('9h-12h')
        
        
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/11')

        schedule_form = response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 11
        schedule_form['end_time'] = 15

        response = schedule_form.submit()
        
        # check on the schedule page
        response.mustcontain('9h-15h')


    def test_merge_adjacent_times(self):
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)

        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/9')

        schedule_form = response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 9
        schedule_form['end_time'] = 12

        response = schedule_form.submit()
        
        # check on the schedule page
        response.mustcontain('9h-12h')
        
        
        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/9')

        schedule_form = response.forms['schedule_form']
        schedule_form['day'] = 'tuesday'
        schedule_form['start_time'] = 12
        response = schedule_form.submit()
        # check on the schedule page
        response.mustcontain('9h-13h')



        
    def test_end_time_in_range(self):
        # for example when you click on 8pm +4 hours, end_time should max out at 10pm
        self.self_signup_provider(self._TEST_PROVIDER_EMAIL, self._TEST_PROVIDER_VANITY_URL)

        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL)

        # click on a button
        response = self.testapp.get('/provider/schedule/' + self._TEST_PROVIDER_VANITY_URL + '/add/tuesday/20')
        
        response.mustcontain('<option selected value="20">20h</option>')
        response.mustcontain('<option selected value="22">22h</option>')
        response.mustcontain('<option selected value="tuesday">Mardi</option>')


if __name__ == "__main__":
    unittest.main()
    
    
