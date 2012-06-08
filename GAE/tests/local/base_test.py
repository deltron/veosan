import unittest
from google.appengine.ext import testbed
import logging
from StringIO import StringIO


class BaseTestCase(unittest.TestCase):
    
    def setUp(self):
        print('setup ' + self._testMethodName)
        logging.basicConfig(level=logging.DEBUG)
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        # mail stubs
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        # set up the logger
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        # en francais

    def tearDown(self):
        print('tearDown ' + self._testMethodName)
        self.testbed.deactivate()
        # close down the logger
        self.handler.flush()
        self.log.removeHandler(self.handler)
        self.handler.close()
        print('-------------------------------')