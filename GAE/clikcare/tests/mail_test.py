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
        testEmail = 'phil@gmail.com'
        patient = Patient()
        patient.email = testEmail
        patient.put()
        provider = Provider()
        provider.firstName = u"Robert (Test)"
        provider.lastName = u"Lang"
        provider.category = u"physiotherapy"
        provider.put()
        booking = Booking()
        booking.patient = patient
        booking.provider = provider
        booking.dateTime = datetime.now()
        booking.put()
        mail.emailBooking(booking)
        messages = self.mail_stub.get_sent_messages(to=testEmail)
        logging.info("sent messages: " + str(messages))
        self.assertEqual(1, len(messages))
        self.assertEqual(testEmail, messages[0].to)