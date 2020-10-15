from maintcal.tests.lib import MaintcalUnitTest

from maintcal.lib.date import parse_str_date
from datetime import datetime

class TestDateSanity(MaintcalUnitTest):

    def local_setup(self):
        # Skip db inserts
        pass

    def test_good(self):
        good_str = "05/08/2008 12:00 AM"
        self.assertEqual(datetime(2008,5,8,0,0), parse_str_date(good_str))

    def test_good_no_zeros(self):
        good_str = "5/8/2008 1:00 AM"
        self.assertEqual(datetime(2008,5,8,1,0), parse_str_date(good_str))

    def test_good_lowercase_merdians(self):
        good_str = "5/8/2008 1:00 Am"
        self.assertEqual(datetime(2008,5,8,1,0), parse_str_date(good_str))

    def test_bad_garbage(self):
        bad_str = "lsjdflkjsdflkjs"
        self.assertRaises(ValueError, parse_str_date, bad_str)

    def test_bad_format(self):
        bad_str =  "5-8-20081:00"
        self.assertRaises(ValueError, parse_str_date, bad_str)

    def test_bogus_date(self):
        bad_str = "5/32/2008 1:00 AM"
        self.assertRaises(ValueError, parse_str_date, bad_str)

    def test_bogus_time(self):
        bad_str = "5/31/2008 41:00 AM"
        self.assertRaises(ValueError, parse_str_date, bad_str)

    def test_bogus_datetime(self):
        bad_str = "9/31/2008 41:00 AM"
        self.assertRaises(ValueError, parse_str_date, bad_str)

    def test_good_underbounds(self):
        bad_str = "0/0/0 0:00 AM"
        self.assertRaises(ValueError, parse_str_date, bad_str)

    def test_good_overbounds(self):
        bad_str = "1/1/10000 1:00 AM"
        self.assertRaises(ValueError, parse_str_date, bad_str)
