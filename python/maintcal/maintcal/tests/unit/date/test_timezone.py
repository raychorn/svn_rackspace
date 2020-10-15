from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from maintcal.lib.date.timezone import TimezoneType, get_timezone_type
from datetime import datetime, timedelta

class TestTzFile(MaintcalUnitTest):

    def test_bogus_timezone_name(self):
        self.assertRaises( ValueError, get_timezone_type, timezone_name = 'blah')    

    def test_get_timezone_type(self):
        tzfile = get_timezone_type( 'America/Chicago' )
    
        if tzfile == None:
            self.fail()
        
    def testfind_timezone_info_utc(self):

        # Just as a reminder, all these START date times are UTC
        tzfile = get_timezone_type( 'America/Chicago' )

        # Jan 2nd
        maintcal_datetime = MaintcalDatetime(2009, 1, 2, 9, 4, 5)
        self.assertEqual(tzfile.find_timezone_info_utc( maintcal_datetime ), 
                TimezoneType(offset=-21600, delta=timedelta(-1, 64800), isdst=0, abbr='CST', isstd=False, isgmt=False) )
       
        # This is in UTC so this is actually Oct 31, 20:59:59 CDT -5 
        maintcal_datetime = MaintcalDatetime(2009, 11, 1, 1, 59, 59)
        self.assertEqual(tzfile.find_timezone_info_utc( maintcal_datetime ), 
                TimezoneType(offset=-18000, delta=timedelta(-1, 68400), isdst=1, abbr='CDT', isstd=False, isgmt=False) )

    def testfind_timezone_info_utc_nov_case(self):

        # Just as a reminder, all these START date times are UTC
        tzfile = get_timezone_type( 'America/Chicago' )

        maintcal_datetime = MaintcalDatetime(2009, 11, 1, 6, 59, 59)
        self.assertEqual(tzfile.find_timezone_info_utc( maintcal_datetime ), 
                TimezoneType(offset=-18000, delta=timedelta(-1, 68400), isdst=1, abbr='CDT', isstd=False, isgmt=False) )

        maintcal_datetime = MaintcalDatetime(2009, 11, 1, 7, 00, 00)
        self.assertEqual(tzfile.find_timezone_info_utc( maintcal_datetime ), 
                TimezoneType(offset=-21600, delta=timedelta(-1, 64800), isdst=0, abbr='CST', isstd=False, isgmt=False) )

    def test_find_timezone_info_utc_mar_case(self):

        # Just as a reminder, all these START date times are UTC
        tzfile = get_timezone_type( 'America/Chicago' )

        maintcal_datetime = MaintcalDatetime(2009, 3, 8, 7, 59, 59)
        self.assertEqual(tzfile.find_timezone_info_utc( maintcal_datetime ), 
                TimezoneType(offset=-21600, delta=timedelta(-1, 64800), isdst=0, abbr='CST', isstd=False, isgmt=False) )

        maintcal_datetime = MaintcalDatetime(2009, 3, 8, 8, 00, 00)
        self.assertEqual(tzfile.find_timezone_info_utc( maintcal_datetime ), 
                TimezoneType(offset=-18000, delta=timedelta(-1, 68400), isdst=1, abbr='CDT', isstd=False, isgmt=False) )

    def test_find_timezone_info_utc_nov_case_st_john(self):

        # Just as a reminder, all these START date times are UTC
        tzfile = get_timezone_type( 'America/St_Johns' )

        maintcal_datetime = MaintcalDatetime(2009, 11, 01, 02, 30, 59)
        self.assertEqual(tzfile.find_timezone_info_utc( maintcal_datetime ), 
                TimezoneType(offset=-9000, delta=timedelta(-1, 77400), isdst=1, abbr='NDT', isstd=False, isgmt=False) )

        #maintcal_datetime = MaintcalDatetime(2009, 3, 8, 8, 00, 00)
        #self.assertEqual(tzfile.find_timezone_info_utc( maintcal_datetime ), 
                #TimezoneType(offset=-18000, delta=timedelta(-1, 68400), isdst=1, abbr='CDT', isstd=False, isgmt=False) )


