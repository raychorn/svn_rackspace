#!/usr/bin/python
"""
This is our test runner.

"""
# Fix our path

import sys
import os

# put the root maintcal dir in the python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

from optparse import OptionParser

from maintcal import tests

# specifically ignore an auth warning
import warnings
warnings.filterwarnings('ignore', 'AuthKit middleware has been turned off by the config option authkit.setup.enable')

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-q", "--quiet",
            action="store_true", dest="quiet", default=False)
    # If this is passed, it will only run this test
    parser.add_option("-f", "--test_file",
            action="store", type="string", dest="test_file", default='')
    # If this is passed, it will only run this test method
    parser.add_option("-m", "--test_method",
            action="store", type="string", dest="test_method", default='')
    # drop and recreate maintcal_test database schema
    parser.add_option("-s", "--refresh_schema",
            action="store_true", dest="refresh_schema", default=False)
    # avoid doing the final SQL rollback
    parser.add_option("-R", "--skip-rollback",
            action="store_true", dest="skip_rollback", default=False)
    # run the browser tests
    parser.add_option("-b", "--browser-tests",
            action="store_true", dest="browser_tests", default=False)
    (options, args) = parser.parse_args()

    if len(args) > 0:
        options.test_file = args[0]
        if len(args) > 1:
            options.test_method = args[1]

    tests.conf_dir = tests.setupTestEnvironment.setup_for_paste(options)

    # don't import runner until we have set up the test environment
    from maintcal.tests.lib import runner

    tr = runner.TestRunner(options, root_dir=root_dir)
    tr.run()
    tr.print_results()

