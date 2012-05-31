#!/usr/bin/python
import optparse
import sys
import os
# Install the Python unittest2 package before you run this script.
import unittest2
import BeautifulSoup

# IN APTANA
# Run -> Run As -> Python Run

USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules"""


def main(sdk_path, test_path):
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
    # Test Beautiful Soup import
    print 'Using BeautifulSoup version ' + BeautifulSoup.__version__
    # collect and un all tests
    suite = unittest2.loader.TestLoader().discover(start_dir=test_path, pattern='*_test.py')
    unittest2.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    #if len(args) != 2:
    #    print 'Error: Exactly 2 arguments required.'
    #    parser.print_help()
    #    sys.exit(1)
    #SDK_PATH = args[0]
    #TEST_PATH = args[1]
    
    
    # Probably a better way to find this
    SDK_PATH = "/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine"


    # Note : uncomment local to run those as well. I commented it to focus on integration
    TEST_PATH = [ #"local",
                  "integration"]
    
    for t in TEST_PATH:
        main(SDK_PATH, t)
    
    