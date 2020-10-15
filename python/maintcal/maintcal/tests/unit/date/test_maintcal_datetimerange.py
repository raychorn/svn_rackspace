from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from maintcal.lib.date.maintcal_datetimerange import MaintcalDatetimeRange
import datetime

class TestMaintcalDatetimeRange(MaintcalUnitTest):
    def local_setup(self):
        pass

    def local_teardown(self):
        pass

    def test_equal_datetimeranges(self):
        the_datetime = MaintcalDatetime(2009, 1, 1, 2, 4, 10)
        the_other_datetime = MaintcalDatetime(2010, 1, 1, 3, 5, 11)
        range_one = MaintcalDatetimeRange(the_datetime, the_other_datetime)
        range_two = MaintcalDatetimeRange(the_datetime, the_other_datetime)

        self.assertEqual(range_one, range_two)

    def test_inequal_datetimeranges(self):
        the_datetime = MaintcalDatetime(2009, 1, 1, 2, 4, 10)
        the_other_datetime = MaintcalDatetime(2010, 1, 1, 3, 5, 11)
        range_one = MaintcalDatetimeRange(the_datetime, the_datetime)
        range_two = MaintcalDatetimeRange(the_datetime, the_other_datetime)

        self.assertNotEqual(range_one, range_two)

    def test_duration_in_minutes(self):
        the_datetime = MaintcalDatetime(2009, 1, 1, 1, 0, 0)
        the_other_datetime = MaintcalDatetime(2009, 1, 1, 2, 30, 30)

        range_one = MaintcalDatetimeRange(the_datetime, the_other_datetime)

        # difference in minutes should be 90.5

        self.assertEqual(90.5, range_one.duration_in_minutes())

    def test_get_javascript_time_tuples(self):
        the_datetime = MaintcalDatetime(2009, 1, 1, 1, 0, 0)
        the_other_datetime = MaintcalDatetime(2009, 1, 1, 2, 30, 30)

        range_one = MaintcalDatetimeRange(the_datetime, the_other_datetime)

        self.assertEqual( range_one.get_javascript_time_tuples('US/Central'),
                [(2008, 12, 31, 19, 0, 0, -21600, 'US/Central', 'CST',0), (2008, 12, 31, 20, 30, 30, -21600, 'US/Central', 'CST',0)] )
        
