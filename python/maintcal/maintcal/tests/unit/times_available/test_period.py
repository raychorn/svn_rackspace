from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.times_available.period import Period
from datetime import datetime, date, timedelta

class TestPeriod(MaintcalUnitTest):
    def local_setup(self):
        MaintcalUnitTest.local_setup(self)
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 5, 0), datetime(2009, 9, 4, 10, 30))
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 7, 0), datetime(2009, 9, 4, 11, 30))
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 11, 0), datetime(2009, 9, 4, 18, 0))
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 22, 0), datetime(2009, 9, 5, 2, 0))
        self.dh.insertScheduledService(1, datetime(2009, 9, 3, 22, 0), datetime(2009, 9, 5, 2, 0))

    def test_calculateStartAndEndTimes(self):
        test_period = Period(date(2009, 1, 2), 60, 120, 2)
        self.assertEqual(datetime(2009, 1, 2, 1), test_period.start_time)        
        self.assertEqual(datetime(2009, 1, 2, 2), test_period.end_time)        

    def test_calculateDepth(self):
        test_period = Period(date(2009, 1, 2), 0, 30, 1)
        self.assertEqual(1, test_period.depth)        

        test_period = Period(date(2009, 1, 2), 0, 30, 2)
        self.assertEqual(2, test_period.depth)        

        test_period = Period(date(2009, 1, 2), 0, 60, 2)
        self.assertEqual(1, test_period.depth)        

        test_period = Period(date(2009, 1, 2), 0, 60, 4)
        self.assertEqual(2, test_period.depth)        

        test_period = Period(date(2009, 1, 2), 0, 60, 8)
        self.assertEqual(4, test_period.depth)        

        test_period = Period(date(2009, 1, 2), 0, 60, 16)
        self.assertEqual(8, test_period.depth)        

        test_period = Period(date(2009, 1, 2), 60, 120, 16)
        self.assertEqual(8, test_period.depth)        

        test_period = Period(date(2009, 1, 2), 0, 30, 3)
        self.assertEqual(3, test_period.depth)        

    def test_bitstringForDepth(self):
        test_period = Period(date(2009, 1, 2), 0, 30, 1)
        self.assertEqual('1', test_period.bitstringForDepth(0))        

        return

        # TODO make this test normalizing and flattening behavior 

        # Try to create a period that would respond with
        # 111000
        # 000111  and then make it respond with 111111


        self.assertEqual('111000', test_period.bitString(0))        
        self.assertEqual('000111', test_period.bitString(1))        

        self.assertEqual('111111', test_period.bitString())        

        Period(depth=2, masks=['111000', '000111']).normalize()


        # use case
        #
        # 1 period with a length of 3 quanta and a depth of 2
        # 1 period with a length of 4 quanta and a depth of 3
        #
        # use case: schedule new service with a quanta of 5
        # if two services of quanta 4 have already been applied to the second period
        #
        # simpler use case: schedule a new service with a quanta of 5


