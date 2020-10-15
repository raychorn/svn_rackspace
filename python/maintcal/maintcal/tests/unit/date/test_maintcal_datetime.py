from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.date.maintcal_date import MaintcalDate
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
import datetime
from datetime import timedelta, datetime, date

class TestMaintcalDatetime(MaintcalUnitTest):
    def local_setup(self):
        pass

    def local_teardown(self):
        pass

    def test_python_date_conversion(self):
        python_date = date(2009, 2, 3)
        maintcal_datetime = MaintcalDatetime.from_python_date(python_date)
        self.assertEqual(python_date, maintcal_datetime.to_python_date())
        
    def test_python_datetime_conversion(self):
        python_datetime = datetime(2009, 2, 3, 4, 5, 6, 0)
        maintcal_datetime = MaintcalDatetime.from_python_datetime(python_datetime)

        self.assertEqual(python_datetime, maintcal_datetime.to_python_datetime())

    def test_maintcal_date_conversion(self):
        date = MaintcalDate(2009, 2, 3)
        datetime = MaintcalDatetime.from_date(date)

        self.assertEqual(date, datetime.to_date())

    def test_comparison_of_two_equal_maintcal_datetimes(self):
        datetime_one = MaintcalDatetime(2009, 2, 3, 4, 5, 6)
        datetime_two = MaintcalDatetime(2009, 2, 3, 4, 5, 6)
    
        self.assertEqual(datetime_one, datetime_two)

    def test_to_tuple(self):
        datetime_one = MaintcalDatetime(2009, 2, 3, 4, 5, 6)
        self.assertEqual( datetime_one.to_tuple(), (2009, 2, 3, 4, 5, 6))

    def test_to_dict(self):
        datetime_one = MaintcalDatetime(2009, 2, 3, 4, 5, 6)
        self.assertEqual( datetime_one.to_dict(), {'year':2009, 'month':2, 'day':3, 'hour':4, 'minute':5, 'second':6})
   
    def test_is_leap_year(self):
        self.assertEqual( MaintcalDatetime._is_leap( 2009 ), False )
        self.assertEqual( MaintcalDatetime._is_leap( 2008 ), True )

    def test_days_before_month(self):
        self.assertEqual( MaintcalDatetime._days_before_month( 2009, 2 ), 31 )
        # 2008 is a leap year, so feb has an extra day
        self.assertEqual( MaintcalDatetime._days_before_month( 2008, 3 ), 60 )

    def test_days_before_year(self):
        self.assertEqual( MaintcalDatetime._days_before_year( 1 ), 0 )
        self.assertEqual( MaintcalDatetime._days_before_year( 2 ), 365 )
        self.assertEqual( MaintcalDatetime._days_before_year( 2009 ), 733407 )
        self.assertEqual( MaintcalDatetime._days_before_year( 2008 ), 733041 )
        # 733407 - 733041 = 366 because 2008 is a leap year

    def test_to_ordinal(self):
        # Start of the Era
        datetime_one = MaintcalDatetime(1, 0, 0, 0, 0, 0)
        self.assertEqual( datetime_one.to_ordinal(), 0 )

        # Date chosen at random
        datetime_one = MaintcalDatetime(2009, 2, 3, 0, 0, 0)
        self.assertEqual( datetime_one.to_ordinal(), 733441 )

        # Plus 1 day
        datetime_one = MaintcalDatetime(2009, 2, 4, 0, 0, 0)
        self.assertEqual( datetime_one.to_ordinal(), 733442 )

        # Plus 1 Month on a non-leap year
        datetime_one = MaintcalDatetime(2009, 3, 4, 0, 0, 0)
        self.assertEqual( datetime_one.to_ordinal(), 733470 )
       
        # Plus 1 year on a non-leap year
        datetime_one = MaintcalDatetime(2010, 3, 4, 0, 0, 0)
        self.assertEqual( datetime_one.to_ordinal(), 733835 )

    def test_to_timestamp(self):
        # The beginning of time ( according to unix ) UTC
        maintcal_datetime_one = MaintcalDatetime(1970, 01, 01, 0, 0, 0)
        self.assertEquals( maintcal_datetime_one.to_timestamp(), 0 )

        maintcal_datetime_one = MaintcalDatetime(1970, 01, 01, 0, 1, 0)
        self.assertEquals( maintcal_datetime_one.to_timestamp(), 60 )

        maintcal_datetime_one = MaintcalDatetime(1970, 01, 01, 1, 0, 0)
        self.assertEquals( maintcal_datetime_one.to_timestamp(), 3600 )

        maintcal_datetime_one = MaintcalDatetime(1970, 01, 02, 0, 0, 0)
        self.assertEquals( maintcal_datetime_one.to_timestamp(), 86400 )

        maintcal_datetime_one = MaintcalDatetime(1970, 02, 01, 0, 0, 0)
        self.assertEquals( maintcal_datetime_one.to_timestamp(), 2678400 )

        maintcal_datetime_one = MaintcalDatetime(1971, 01, 01, 0, 0, 0)
        self.assertEquals( maintcal_datetime_one.to_timestamp(), 31536000 )

        maintcal_datetime_one = MaintcalDatetime(2010, 3, 4, 0, 0, 0)
        self.assertEquals( maintcal_datetime_one.to_timestamp(), 1267660800 )
        
        maintcal_datetime_one = MaintcalDatetime(2010, 3, 4, 0, 0, 1)
        self.assertEquals( maintcal_datetime_one.to_timestamp(), 1267660801 )

    def test_from_timestamp(self):
        self.assertEquals( MaintcalDatetime.from_timestamp(0), MaintcalDatetime(1970, 01, 01, 0, 0, 0) )

        self.assertEquals( MaintcalDatetime.from_timestamp(60), MaintcalDatetime(1970, 01, 01, 0, 1, 0) )

        self.assertEquals( MaintcalDatetime.from_timestamp(3600), MaintcalDatetime(1970, 01, 01, 1, 0, 0) )

        self.assertEquals( MaintcalDatetime.from_timestamp(86400), MaintcalDatetime(1970, 01, 02, 0, 0, 0) )

        self.assertEquals( MaintcalDatetime.from_timestamp(2678400), MaintcalDatetime(1970, 02, 01, 0, 0, 0) )

        self.assertEquals( MaintcalDatetime.from_timestamp(31536000), MaintcalDatetime(1971, 01, 01, 0, 0, 0) )

        self.assertEquals( MaintcalDatetime.from_timestamp(1267660800), MaintcalDatetime(2010, 3, 4, 0, 0, 0) )

        self.assertEquals( MaintcalDatetime.from_timestamp(1267660801), MaintcalDatetime(2010, 3, 4, 0, 0, 1) )

    def test_to_utc(self):
        maintcal_datetime = MaintcalDatetime(1971, 01, 01, 0, 0, 0)

        self.assertEquals( maintcal_datetime.to_utc( timedelta( -1 ) ),  MaintcalDatetime(1971, 01, 02, 0, 0, 0) )

        self.assertEquals( maintcal_datetime.to_utc( timedelta( 1 ) ),  MaintcalDatetime(1970, 12, 31, 0, 0, 0) )

    def test_to_localtime(self):
        maintcal_datetime = MaintcalDatetime(1971, 01, 01, 0, 0, 0)
        
        self.assertEquals( maintcal_datetime.to_localtime( timedelta( 1 ) ),  MaintcalDatetime(1971, 01, 02, 0, 0, 0) )

        self.assertEquals( maintcal_datetime.to_localtime( timedelta( -1 ) ),  MaintcalDatetime(1970, 12, 31, 0, 0, 0) )

        self.assertEquals( maintcal_datetime.to_localtime( timedelta( -1, 3600 ) ),  MaintcalDatetime(1970, 12, 31, 01, 0, 0) )

        self.assertEquals( maintcal_datetime.to_localtime( timedelta( -1, 3600 * 6 ) ),  MaintcalDatetime(1970, 12, 31, 06, 0, 0) )

        self.assertEquals( maintcal_datetime.to_localtime( timedelta( 0, -3600 ) ),  MaintcalDatetime(1970, 12, 31, 23, 0, 0) )

    def test_to_local_leap_year(self):

        # 2008 is a leap year
        maintcal_datetime = MaintcalDatetime(2008, 03, 01, 0, 0, 0)
        self.assertEquals( maintcal_datetime.to_localtime( timedelta( -1, 3600 ) ),  MaintcalDatetime(2008, 02, 29, 01, 0, 0) )
        
        # 2009 is not a leap year
        maintcal_datetime = MaintcalDatetime(2009, 03, 01, 0, 0, 0)
        self.assertEquals( maintcal_datetime.to_localtime( timedelta( -1, 3600 ) ),  MaintcalDatetime(2009, 02, 28, 01, 0, 0) )


