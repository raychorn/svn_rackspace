from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from maintcal.lib.date.timezone_renderer import TimezoneRenderer, TimezoneRendererPro, TimezoneRendererTzFile
from datetime import datetime

class TestTimezoneRenderer(MaintcalUnitTest):
    def local_setup(self):
        pass

    def local_teardown(self):
        pass
        
    def test_build_sql_query(self):
        timezone_name = 'US/Central'
        tr = TimezoneRendererPro(timezone_name)
        maintcal_datetime = MaintcalDatetime(2009, 1, 2, 9, 4, 5)
        self.assertEquals( tr._build_sql_query( [ MaintcalDatetime(2009, 1, 2, 9, 4, 5), MaintcalDatetime(2009, 1, 2, 9, 4, 5) ] ), 
                "SELECT TIMESTAMP WITH TIME ZONE '2009-1-2 9:4:5 UTC' AT TIME ZONE 'US/Central'," \
                "TIMESTAMP WITH TIME ZONE '2009-1-2 9:4:5 UTC' AT TIME ZONE 'US/Central'" )
       
    def test_get_javascript_time_tuples(self):
        timezone_name = 'US/Central'
        tr = TimezoneRendererPro(timezone_name)
        self.assertEquals( tr.get_javascript_time_tuples( [ MaintcalDatetime(2009, 1, 2, 9, 4, 5), MaintcalDatetime(2009, 1, 2, 9, 4, 5) ] ),
            [(2009, 1, 2, 3, 4, 5, -21600, 'US/Central', 'CDT'), (2009, 1, 2, 3, 4, 5, -21600, 'US/Central', 'CDT')] )
        # Test passing in None
        self.assertEquals( tr.get_javascript_time_tuples( [ None ] ),
            [(0, 0, 0, 0, 0, 0, 0, u'UTC', 'UTC')] )
         
    def test_pro_conversion_speed(self):
        maintcal_datetime = MaintcalDatetime(2009, 1, 2, 9, 4, 5)
        timezone_name = 'US/Central'
   
        maintcal_datetime_list = []
        for i in range(1000):
            maintcal_datetime_list.append( MaintcalDatetime(2009, 1, 2, 9, 4, 5) )

        tr = TimezoneRendererPro(timezone_name)
        result = tr.get_javascript_time_tuples( maintcal_datetime_list )
        #print result[0], result[999]


    # TimezoneRendereTzFile Tests
    # -------------------------------------------------------------
    def test_bogus_timezone_name(self):
        self.assertRaises( ValueError, TimezoneRendererTzFile, timezone_name = 'blah')
        
    def test_as_timezone(self):
        timezone_name = 'US/Central'

        # This is January 2nd, 09:04:05 UTC
        maintcal_datetime = MaintcalDatetime(2009, 1, 2, 9, 4, 5)
        test_time_tuple = TimezoneRendererTzFile(timezone_name).as_timezone(maintcal_datetime)
        # Should convert to January 2nd, 03:04:05 Central Standard Time
        self.assertEqual( test_time_tuple, (MaintcalDatetime(2009,01,02,03,04,05), -21600, 0, 'CST') )

    def test_tzfile_simple_conversion(self):
        timezone_name = 'US/Central'

        # This is January 2nd, 09:04:05 UTC
        maintcal_datetime = MaintcalDatetime(2009, 1, 2, 9, 4, 5)
        test_time_tuple = TimezoneRendererTzFile(timezone_name)._get_javascript_time_tuple(maintcal_datetime)
        # Should convert to January 2nd, 03:04:05 Central Standard Time
        self.assertEqual((2009, 1, 2, 3, 4, 5, -21600, timezone_name, 'CST',0), test_time_tuple)
        
    def test_march_cdt(self):
        timezone_name = 'US/Central'

        # This is March 8th 7:59:59 PM UTC
        maintcal_datetime = MaintcalDatetime(2009, 3, 8, 7, 59, 59)
        test_time_tuple = TimezoneRendererTzFile(timezone_name)._get_javascript_time_tuple(maintcal_datetime)
        # Should Convert to March 8th 1:59:59 PM Central Standard Time
        self.assertEqual((2009, 3, 8, 1, 59, 59, -21600, timezone_name, 'CST',0), test_time_tuple)

        # This is March 8th 8:00:00 PM UTC
        maintcal_datetime = MaintcalDatetime(2009, 3, 8, 8, 00, 00)
        test_time_tuple = TimezoneRendererTzFile(timezone_name)._get_javascript_time_tuple(maintcal_datetime)
        # Should Convert to March 8th 3:00:00 PM Central DaylightSavings Time
        self.assertEqual((2009, 3, 8, 3, 00, 00, -18000, timezone_name, 'CDT',1), test_time_tuple)

    def test_nov_cst(self):
        timezone_name = 'US/Central'

        # This is Nov 1st 6:59:59 PM UTC
        maintcal_datetime = MaintcalDatetime(2009, 11, 1, 6, 59, 59)
        test_time_tuple = TimezoneRendererTzFile(timezone_name)._get_javascript_time_tuple(maintcal_datetime)
        # Should Convert to Nov 1st 1:59:59 PM Central Standard Time
        self.assertEqual((2009, 11, 1, 1, 59, 59, -18000, timezone_name, 'CDT',1), test_time_tuple)

        # This is Nov 1st 7:59:59 PM UTC
        maintcal_datetime = MaintcalDatetime(2009, 11, 1, 7, 59, 59)
        test_time_tuple = TimezoneRendererTzFile(timezone_name)._get_javascript_time_tuple(maintcal_datetime)
        # Should Convert to Nov 1st 1:59:59 PM Central DaylightSavings Time
        self.assertEqual((2009, 11, 1, 1, 59, 59, -21600, timezone_name, 'CST',0), test_time_tuple)

    def test_tz_file_get_javascript_time_tuples(self):
        timezone_name = 'US/Central'
        tr = TimezoneRendererTzFile(timezone_name)
        self.assertEquals( tr.get_javascript_time_tuples( [ MaintcalDatetime(2009, 1, 2, 9, 4, 5), 
                                                            MaintcalDatetime(2009, 1, 2, 9, 4, 5) ] ),
                                                        [(2009, 1, 2, 3, 4, 5, -21600, 'US/Central', 'CST',0), 
                                                         (2009, 1, 2, 3, 4, 5, -21600, 'US/Central', 'CST',0)] )
        # Test passing in None
        self.assertEquals( tr.get_javascript_time_tuples( [ None ] ), [(0, 0, 0, 0, 0, 0, 0, u'UTC', 'UTC')] )

    def test_tzfile_conversion_speed(self):
        maintcal_datetime = MaintcalDatetime(2009, 1, 2, 9, 4, 5)
        timezone_name = 'US/Central'
   
        maintcal_datetime_list = []
        for i in range(1000):
            maintcal_datetime_list.append( MaintcalDatetime(2009, 1, 2, 9, 4, 5) )

        tr = TimezoneRendererTzFile(timezone_name)
        result = tr.get_javascript_time_tuples( maintcal_datetime_list )


