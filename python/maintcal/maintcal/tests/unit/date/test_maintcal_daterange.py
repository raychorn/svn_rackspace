from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.date.maintcal_date import MaintcalDate
from maintcal.lib.date.maintcal_daterange import MaintcalDateRange
import datetime

class TestMaintcalDateRange(MaintcalUnitTest):
    def local_setup(self):
        pass

    def local_teardown(self):
        pass

    def test_equal_dateranges(self):
        the_date = MaintcalDate(2009, 1, 1)
        the_other_date = MaintcalDate(2010, 1, 1)
        range_one = MaintcalDateRange(the_date, the_other_date)
        range_two = MaintcalDateRange(the_date, the_other_date)

        self.assertEqual(range_one, range_two)


    def test_inequal_dateranges(self):
        the_date = MaintcalDate(2009, 1, 1)
        the_other_date = MaintcalDate(2010, 1, 1)
        range_one = MaintcalDateRange(the_date, the_date)
        range_two = MaintcalDateRange(the_date, the_other_date)

        self.assertNotEqual(range_one, range_two)


    def test_dates_iteration(self):
        the_date = MaintcalDate(2009, 1, 1)
        the_other_date = MaintcalDate(2009, 2, 1)
        range_one = MaintcalDateRange(the_date, the_other_date)

        count = 0
        for some_date in range_one.dates():
            count += 1

        # 31 days in jan + 1 day in feb
        self.assertEqual(32, count)


