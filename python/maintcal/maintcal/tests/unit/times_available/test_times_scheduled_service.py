from maintcal.tests.lib import MaintcalUnitTest
from maintcal.model import db_sess, ScheduledService

from maintcal.lib.times_available.period import Period
from datetime import datetime, date, timedelta

class TestScheduledService(MaintcalUnitTest):
    def local_setup(self):
        MaintcalUnitTest.local_setup(self)
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 5, 0), datetime(2009, 9, 4, 10, 30))
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 7, 0), datetime(2009, 9, 4, 11, 30))
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 11, 0), datetime(2009, 9, 4, 18, 0))
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 22, 0), datetime(2009, 9, 5, 2, 0))
        self.dh.insertScheduledService(1, datetime(2009, 9, 3, 22, 0), datetime(2009, 9, 5, 2, 0))

    def getScheduledService(self, calendar_id, start, end):
        new_ss = ScheduledService('', calendar_id, 0)
        new_ss.start_time = start
        new_ss.end_time = end

        return new_ss

    def test_overlaps(self):
        # period is completely contained by the service
        test_service = self.getScheduledService(1, datetime(2009, 1, 2, 1, 0), datetime(2009, 1, 3, 2, 0))
        test_period = Period(date(2009, 1, 2), 60, 120, 1)
        self.assertTrue(test_service.overlaps(test_period))

        # period is adjacent to service
        test_service = self.getScheduledService(1, datetime(2009, 1, 2, 1, 0), datetime(2009, 1, 3, 2, 0))
        test_period = Period(date(2009, 1, 3), 120, 240, 1)
        self.assertFalse(test_service.overlaps(test_period))
        
        # period starts before service, but overlaps it
        test_service = self.getScheduledService(1, datetime(2009, 1, 2, 1, 0), datetime(2009, 1, 2, 2, 0))
        test_period = Period(date(2009, 1, 2), 30, 150, 1)
        self.assertTrue(test_service.overlaps(test_period))

    def test_quantaHandledByPeriod(self):
        test_service = self.getScheduledService(1, datetime(2009, 1, 2, 1, 0), datetime(2009, 1, 2, 2, 0))
        test_period = Period(date(2009, 1, 2), 60, 120, 1)
        self.assertEqual(2, test_service.quantaHandledByPeriod(test_period))

        #       A period that has 1 work unit over 30 minutes.
        #           this means that it has a depth of 2 and a length of 1 quanta.
        #           The only way to schedule the entire period is to use 2 services.

    def test_quantaHandledByPeriod_two(self):

        # a 2 hour scheduled service
        test_service = self.getScheduledService(1, datetime(2009, 1, 2, 0, 0), datetime(2009, 1, 2, 2, 0))

        # a period with 1 quanta
        test_period = Period(date(2009, 1, 2), 0, 30, 1)

        self.assertEqual(1, test_service.quantaHandledByPeriod(test_period))



