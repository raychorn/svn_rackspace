from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from maintcal.lib.date.timezone_normalizer import TimezoneNormalizer
from maintcal.lib.date.timezone_normalizer import InvalidDatetimeException
from maintcal.lib.date.timezone_normalizer import AmbiguousDatetimeException
from maintcal.model import db_sess
from datetime import datetime

class TestTimezoneNormalizer(MaintcalUnitTest):
    def local_setup(self):
        pass

    def local_teardown(self):
        pass

    def test_simple_conversion(self):
        python_datetime = datetime(2009, 1, 2, 3, 4, 5)
        target_maintcal_datetime = MaintcalDatetime(2009, 1, 2, 9, 4, 5)
        timezone_name = 'US/Central'

        tn = TimezoneNormalizer(python_datetime, timezone_name)
        test_maintcal_datetime = tn.get_maintcal_datetime()
        self.assertEqual(target_maintcal_datetime, test_maintcal_datetime)

    def test_cross_dst_break(self):
        """ Test to ensure that when a conversion happens across a dst break that it is 
            converted to UTC appropriatly.
        """
        python_datetime = datetime(2009, 3, 16, 3, 0, 0)
        target_maintcal_datetime = MaintcalDatetime(2009, 3, 16, 8, 0, 0)
        timezone_name = 'US/Central'

        tn = TimezoneNormalizer(python_datetime, timezone_name)
        test_maintcal_datetime = tn.get_maintcal_datetime()
        self.assertEqual(target_maintcal_datetime, test_maintcal_datetime)

    def test_conversion_speed(self):
        python_datetime = datetime(2009, 1, 2, 3, 4, 5)
        target_maintcal_datetime = MaintcalDatetime(2009, 1, 2, 9, 4, 5)
        timezone_name = 'US/Central'

        # 15 seconds to do 10000 conversions
        # 2 seconds to do 1000 conversions
        #for i in range(1000):
        #    tn = TimezoneNormalizer(python_datetime, timezone_name)
        #    #print tn.get_maintcal_datetime()
    
    def test_invalid_datetime_error_raised_on_invalid_datetime(self):
        ''' 
            ryan.springer@d-db1:~$ zdump -v US/Central | grep 2009 | grep Mar
            US/Central  Sun Mar  8 07:59:59 2009 UTC = Sun Mar  8 01:59:59 2009 CST isdst=0 gmtoff=-21600
            US/Central  Sun Mar  8 08:00:00 2009 UTC = Sun Mar  8 03:00:00 2009 CDT isdst=1 gmtoff=-18000

            If the client sends us 2:30 US/Central, this is not a validate datetime.
        '''
        invalid_python_datetime = datetime(2009, 3, 8, 2, 30, 0)
        timezone_normalizer = TimezoneNormalizer(invalid_python_datetime, 'US/Central')
        self.assertRaises(InvalidDatetimeException, timezone_normalizer.get_maintcal_datetime)

        invalid_python_datetime = datetime(2009, 3, 8, 0, 30, 0)
        timezone_normalizer = TimezoneNormalizer(invalid_python_datetime, 'America/St_Johns')
        self.assertRaises(InvalidDatetimeException, timezone_normalizer.get_maintcal_datetime)

    def test_invalid_datetime_error_not_raised_on_valid_datetime(self):
        valid_python_datetime = datetime(2009, 4, 8, 2, 30, 0)
        timezone_normalizer = TimezoneNormalizer(valid_python_datetime, 'US/Central')
        try:
            timezone_normalizer.get_maintcal_datetime()
        except:
            self.fail("An exception was raised, this test is failing")

    def test_ambiguous_datetime_us_central(self):
        '''
            ryan.springer@d-db1:~$ zdump -v US/Central | grep 2009 | grep Nov
            US/Central  Sun Nov  1 06:59:59 2009 UTC = Sun Nov  1 01:59:59 2009 CDT isdst=1 gmtoff=-18000
            US/Central  Sun Nov  1 07:00:00 2009 UTC = Sun Nov  1 01:00:00 2009 CST isdst=0 gmtoff=-21600

            If the client sends us 1:30 US/Central, this is an ambiguous datetime.

            It would be great to update this test to handle a known case where the DST shift is greater
            than or less than 60 minutes.
        '''
        ambiguous_python_datetime = datetime(2009, 11, 1, 01, 00, 00)
        timezone_normalizer = TimezoneNormalizer(ambiguous_python_datetime, 'US/Central')
        self.assertRaises(AmbiguousDatetimeException, timezone_normalizer.get_maintcal_datetime)

        ambiguous_python_datetime = datetime(2009, 11, 1, 01, 30, 00)
        timezone_normalizer = TimezoneNormalizer(ambiguous_python_datetime, 'US/Central')
        self.assertRaises(AmbiguousDatetimeException, timezone_normalizer.get_maintcal_datetime)

        ambiguous_python_datetime = datetime(2009, 11, 1, 01, 59, 59)
        timezone_normalizer = TimezoneNormalizer(ambiguous_python_datetime, 'US/Central')
        self.assertRaises(AmbiguousDatetimeException, timezone_normalizer.get_maintcal_datetime)


    def test_ambiguous_datetime_st_johns(self):
        """
            America/St_Johns  Sun Nov  1 02:30:59 2037 UTC = Sun Nov  1 00:00:59 2037 NDT isdst=1 gmtoff=-9000
            America/St_Johns  Sun Nov  1 02:31:00 2037 UTC = Sat Oct 31 23:01:00 2037 NST isdst=0 gmtoff=-12600
        """
        self.broken_test(); return

        ambiguous_python_datetime = datetime(2009, 11, 1, 00, 00, 00)
        timezone_normalizer = TimezoneNormalizer(ambiguous_python_datetime, 'America/St_Johns')
        self.assertRaises(AmbiguousDatetimeException, timezone_normalizer.get_maintcal_datetime)

        # the following test currently fails, Does this really matter for our use case?
        ambiguous_python_datetime = datetime(2009, 11, 1, 23, 01, 00)
        timezone_normalizer = TimezoneNormalizer(ambiguous_python_datetime, 'America/St_Johns')
        self.assertRaises(AmbiguousDatetimeException, timezone_normalizer.get_maintcal_datetime)

        ambiguous_python_datetime = datetime(2009, 11, 1, 00, 00, 59)
        timezone_normalizer = TimezoneNormalizer(ambiguous_python_datetime, 'America/St_Johns')
        self.assertRaises(AmbiguousDatetimeException, timezone_normalizer.get_maintcal_datetime)


    def test_valid_conversions_us_central(self):
        python_datetime = datetime(2009, 11, 1, 2, 00, 00)
        timezone_normalizer = TimezoneNormalizer(python_datetime, 'US/Central')
        # The only time there is a 2am US/Central will be 8am UTC
        self.assertEqual( timezone_normalizer.get_maintcal_datetime(), MaintcalDatetime( 2009, 11, 1, 8, 00, 00 ) )

        python_datetime = datetime(2009, 11, 1, 2, 59, 00)
        timezone_normalizer = TimezoneNormalizer(python_datetime, 'US/Central')
        # The only time there is a 2am US/Central will be 8am UTC
        self.assertEqual( timezone_normalizer.get_maintcal_datetime(), MaintcalDatetime( 2009, 11, 1, 8, 59, 00 ) )

        python_datetime = datetime(2009, 11, 1, 00, 59, 00)
        timezone_normalizer = TimezoneNormalizer(python_datetime, 'US/Central')
        self.assertEqual( timezone_normalizer.get_maintcal_datetime(), MaintcalDatetime( 2009, 11, 1, 5, 59, 00 ) )

    #def test_valid_conversions_st_johns(self):


    def test_ambiguous_datetime_error_not_raised_on_valid_datetime(self):
        valid_python_datetime = datetime(2009, 11, 15, 1)
        timezone_normalizer = TimezoneNormalizer(valid_python_datetime, 'US/Central')
        try:
            timezone_normalizer.get_maintcal_datetime()
        except:
            self.fail("An exception was raised, this test is failing")
