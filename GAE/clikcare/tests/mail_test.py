import unittest
from google.appengine.ext import testbed
import logging
import mail
from datetime import datetime
from data import Provider, Booking, Patient

class DBTestCase(unittest.TestCase):
    def setUp(self):
        print('setup ' + self._testMethodName)
        logging.basicConfig(level=logging.DEBUG)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        # db stubs
        self.testbed.init_datastore_v3_stub()
        # mail stubs
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def tearDown(self):
        print('tearDown ' + self._testMethodName)
        self.testbed.deactivate()
        print('-------------------------------')

    def testEmailBooking(self):
        patient = Patient()
        patient.email = 'phil@gmail.com'
        patient.put()
        booking = Booking()
        booking.patient = patient
        booking.put()
        mail.emailBooking(booking)