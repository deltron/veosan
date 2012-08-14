# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db
import testutil

class PublicProfileTest(BaseTest):
    
    def test_visit_public_profile(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: public view")

    def test_visit_public_profile_self_view(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        self.login_as_provider()

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: self-view")

    def test_visit_public_profile_admin_view(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        self.login_as_admin()

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # by default address is hidden and no booking
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        #self.assert_msg_in_log("Public profile: public view", admin=True)

    def test_disable_enable_show_address(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        
        # hide last name
        public_profile.mustcontain("Fantastic Fox")
                
        public_profile.mustcontain(no="Map")
        public_profile.mustcontain(no="Réservez Maintenant")
        
        # enable the address
        self.login_as_admin()
        enable = self.testapp.post('/admin/provider/feature/address_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Map")
        
        
        # hit it again to disable the address
        disable = self.testapp.post('/admin/provider/feature/address_enabled/' + self._TEST_PROVIDER_VANITY_URL)

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Map")
        
        
    def test_disable_enable_show_booking(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
    
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        
        self.login_as_admin()
        
        public_profile.mustcontain(no="Map")

        
        # enable the booking
        enable = self.testapp.post('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Réservez Maintenant")
        
        
        # hit it again to disable the booking
        disable = self.testapp.post('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)

        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain(no="Réservez Maintenant")
        
        
    def test_book_from_public_profile(self):
        # create a new provider, vanity URL is bobafett
        self.create_complete_provider_profile()
        # check profile
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        # enable the booking
        self.login_as_admin()
        enable = self.testapp.post('/admin/provider/feature/booking_enabled/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile = self.testapp.get('/' + self._TEST_PROVIDER_VANITY_URL)
        public_profile.mustcontain("Fantastic Fox")
        public_profile.mustcontain("Réservez Maintenant")
        schedule_page = public_profile.click(linkid='book_button')
        schedule_page.mustcontain("Choisissez la date et l'heure de votre rendez-vous")
        # find the form for next Monday at 10
        form_id = "form-" + testutil.next_monday_date_string() + "-10"
        form = schedule_page.forms[form_id]
        new_patient_page = form.submit()
        new_patient_page.mustcontain('Nouveau patient')
        #new_patient_page.showbrowser()
    
        # fill patient info
        
        # check confirmation
        
        # check emails
        
        # check provider bookings list
        
        # check patient's booking list
        
        # check admin side bookings
        
        # check event logs
        
        

if __name__ == "__main__":
    unittest.main()
    
    
