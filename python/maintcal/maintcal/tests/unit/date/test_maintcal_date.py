from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.date.maintcal_date import MaintcalDate
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
import datetime

class TestMaintcalDate(MaintcalUnitTest):
    def local_setup(self):
        pass

    def local_teardown(self):
        pass

    def test_python_date_conversion(self):
        python_date = datetime.date(2009, 2, 3)
        maintcal_date = MaintcalDate.from_python_date(python_date)
        self.assertEqual(python_date, maintcal_date.to_python_date())
        
    def test_python_datetime_conversion(self):
        python_datetime = datetime.datetime(2009, 2, 3, 4, 5, 6)
        maintcal_date = MaintcalDate.from_python_datetime(python_datetime)

        truncated_python_datetime = datetime.datetime(2009, 2, 3)
        self.assertEqual(truncated_python_datetime, maintcal_date.to_python_datetime())

    def test_maintcal_datetime_conversion(self):
        datetime = MaintcalDatetime(2009, 1, 1, 12, 10, 10)
        date = MaintcalDate.from_datetime(datetime)

        expected_datetime = MaintcalDatetime(2009, 1, 1, 0, 0, 0) 
        self.assertEqual(expected_datetime, date.to_datetime())

    def test_comparison_to_maintcal_date_with_same_date(self):
        date_one = MaintcalDate(2009, 1, 1)
        date_two = MaintcalDate(2009, 1, 1)

        self.assertEqual(date_one, date_two)
