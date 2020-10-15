from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.date import date_to_datetime
from datetime import date, datetime

class TestDatefunc(MaintcalUnitTest): # smell the func
    def test_date_to_datetime(self):
      test_date = date(2009,1,1)
      test_datetime = datetime(2009, 1, 1)
      self.assertEqual(test_datetime, date_to_datetime(test_date))
