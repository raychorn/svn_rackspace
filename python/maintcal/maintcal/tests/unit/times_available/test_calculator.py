"""
THE MOST IMPORTANT THING TO REMEMBER WHEN TESTING TIMES AVAILABLE IS:

        Possibilites for scheduling a gived service into a given period
            with no blocks and no other schedules:

        max possibilities = (2 * period length in hours + 1) - length of service in quanta

If you decompose the available times for a given date range 
(that is the defaults and exceptions and the already scheduled services), 
into open periods of various lengths, you can use the above formula once 
for each period and add the results together to get the total available times.


=====================================================================================

    Given a period and a service, there are the following possible situations:

           1        2       3

        ps < ss, ps = ss, ps > ss  choose 1 from 3  Choice A
        ps < se, ps = se, ps > se  choose 1 from 3  Choice B

        pe < ss, pe = ss, pe > ss  choose 1 from 3  Choice C
        pe < se, pe = se, pe > se  choose 1 from 3  Choice D

    This yields 3 x 3 x 3 x 3 = 81 possibilities
                if we ignore constraints based on start < end

    Constraints

    If A1
        then B1
        then any C
        then any D

        There are 1 x 1 x 3 x 3 tuples starting with A1

        (1 * 1 * 2 * 3) with A1

        There are 9 A1 tuples

        A1, B1, C123, D123

    If A2
        then B1
        then C3
        then any D
        1 x 1 x 1 x 3

        There are 3 A2 tuples
    
    If A3
        then any B
        then C3
        then any D
    1 x 3 x 1 x 3 = 9

    There are 9 + 3 + 9 = 21 possible combinations:

        A1, B1, C123, D123
        A2, B1, C3, D123
        A3, B123, C3, D123


    A1: period starts before service starts
        implications: ps < se & pe > ss

        ps < ss
        pe < ss

            A1, B1, C1, D1      period before service, implies D1     
                A1, B1, C1, D2      imp
                A1, B1, C1, D3      imp

        ps < ss
        pe = ss

            A1, B1, C2, D1      period ends when service starts, implies D1
                A1, B1, C2, D2      imp
                A1, B1, C2, D3      imp

        ps < ss
        pe > ss
            A1, B1, C3, D1      period ends after service starts, ends before service ends
            A1, B1, C3, D2      ", ends when service ends
            A1, B1, C3, D3      ", ends after service ends

    A2: period starts when service start
        implications: ps < se & pe > ss

        ps = ss
            A2, B1, C3, D1      and ends before service ends 
            A2, B1, C3, D2      and ends when the service ends 
            A2, B1, C3, D3      and ends after the service ends

    A3: period starts after service start
        implications: pe > ss

        ps > se
            A3, B1, C3, D1      period is contained within the service, ending before the service ends
            A3, B1, C3, D2      period is contained within the service, ending when the service ends
            A3, B1, C3, D3      and period overlaps the back end of the service 

                A3, B2, C3, D1      imp 
                A3, B2, C3, D2      imp 
            A3, B2, C3, D3      period starts when service ends and continues on 

                A3, B3, C3, D1      imp 
                A3, B3, C3, D2      imp 
            A3, B3, C3, D3      period occurs after the service 

-----------------------------------------------------------------------------


        8        10
        ps       pe
 5           9
        *        *

   1    2    3   4   5

  ss
  

If ss = 1, then se = 12345    5 possibilities
If ss = 2, then se = 345      3
If ss = 3, then se = 345      3
If ss = 4, then se = 5        1
If ss = 5, then se = 5        1

        5 + 6 + 2 = 11 + 2 = 13

    1,1 1,2 1,3 1,4 1,5
    2,3 2,4 2,5
    3,3 3,4 3,5
    4,5
    5,5


    for all tests, use the same period
    ps = 8
    pe = 10

==========================================================


    things to test:

        build a bitmask for a day

        build a bitmask for a service

        given a bitmask for a service,
            and a bitmask for a day
            return the number of available times







    maintcal.lib.model.calendar

        get default_times, blocked_times, scheduled_services
        delegate them and the PotentialService into the calculator
        return results


    maintcal.lib.times_available.calculator             a method object





    calendar._perform_times_available_query(start_date, end_date, svc_len)





        timesAvailableCalculator._perform_times_available_query(TimesAvailableCalendar, PotentialService)



basic option:

    timesAvailableCalculator._perform_times_available_query(PotentialService, list_of_cal_ids) 


keith option

    from maintcal.lib.times_available.calendar_factory import CalendarFactory

    calendar_list = CalendarFactory(list_of_cal_ids)
    timesAvailableCalculator._perform_times_available_query(PotentialService, calendar_list) 



    schedule :: (cal_id, start_date, end_date, default_times, blocked_times, scheduled_services)


    timesAvailableCalculator._perform_times_available_query :: PotentialService -> [work_queue_info] -> [ (start-datetime, end-datetime) ]

    cal_id :: model.calendar.cal_id


    timesAvailableCalculator._perform_times_available_query :: PotentialService -> [cal_id] -> [ (start-datetime, end-datetime) ]

        [schedule] = Schedule.getSchedules(PotentialService.start_date, PotentialService.end_date, [cal_id])







    available_times = cal._perform_times_available_query(
                            default_times, blocked_times, scheduled_services, start_date, end_date, svc_len, cal_id)

    available_times = cal._perform_times_available_query(calendar, 

    calendar._perform_times_available_query

        calculator._perform_times_available_query(self

        given default_times, blocked_times, scheduled_services, start_date, end_date, svc_len
            - create bitmask for date range from default_times, blocked_times, scheduled_services
                for each day:
                    start with default_times or start with blocked_times
                    apply scheduled_services
                concat to date_range
                this could yield a single object -> date_range_thingy

            - create bitmask for start_date, end_date, svc_len
                this could yield a single object -> potential_service

            - manipulate bitmasks
                date_range_thingy.getTimesAvailable(potential_service) 

            # yield number of available_times

    2 types of tests:

        test the whole thing
        test the parts of the algorithm



    # determine how many available times

    self._testBoundaries(5, 6, BOUNDARY.PERIOD_LEFT)
    self._testBoundaries(5, 8, BOUNDARY.PERIOD_LEFT_RIGHT_EQUAL_LEFT)
    self._testBoundaries(5, 9, BOUNDARY.PERIOD_LEFT_RIGHT_INBETWEEN)
    self._testBoundaries(5, 10, BOUNDARY.PERIOD_LEFT_RIGHT_EQUAL_RIGHT)

# we have a 2 hr period, between 8 and 9
# service might have different lengths for different tuples
[
    # ps in region 1
    (5, 6, 0),
    (5, 8, 0),
    (5, 9, 1), # this service takes first hour of our period
    (5, 8, 0),
    (5, 8, 0),
    # ps in region 2 
    (5, 6, 0),
    (5, 8, 0),
    (5, 8, 0),
    # ps in region 3
    (5, 6, 0),
    (5, 8, 0),
    (5, 8, 0),
    # ps in region 4
    (5, 6, 0),
    # ps in region 5
    (5, 6, 0),
]




"""
from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.times_available.calculator import Calculator
from maintcal.lib.times_available.times_available_query import TimesAvailableQuery
from maintcal.model import db_sess, ScheduledService, AvailableDefaults, AvailableExceptions
from datetime import datetime, date, timedelta
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from maintcal.lib.times_available import granularity_in_minutes

class TestCalculator(MaintcalUnitTest):

    #def setUp(self):
    #pass

    #def tearDown(self):
    #    pass

    #def local_setup(self):
    #    #MaintcalUnitTest.local_setup(self)
    #    pass

    #    # Make sure that we do not have any scheduled services
    #    #db_sess.execute("TRUNCATE scheduled_service CASCADE;")
    #    #db_sess.commit()

    #def application_teardown(self):
    #    pass

    def assertTimesAvailable(self, start_date, end_date, svc_len, result, not_avail = False, is_avail = False, calendar_ids = [1]):
        """
        NOTE: svc_len is in hours
        """
        # NOTE: seconds in the end time are currently ignored

        calculator = Calculator()
        service_length_in_hours = float(svc_len)
        #print repr(service_length_in_hours)

        service_length_in_minutes = service_length_in_hours * 60
        #print repr(service_length_in_minutes)

        service_length_in_quanta = int(service_length_in_minutes / granularity_in_minutes())

        #print repr(service_length_in_quanta)
        query = TimesAvailableQuery(start_date, end_date, service_length_in_quanta)
        available_start_times = calculator._perform_times_available_query(query, calendar_ids)

        #print repr(available_start_times)
        #print 'Avail Times: '
        #for t in available_start_times:
        #    #print t

        self.assertEqual(result, len(available_start_times))

        if not_avail:
            for item in not_avail:
                if item in available_start_times:
                    self.fail("Time: %s is an available time, it should NOT be available" % (item))

        if is_avail:
            for item in is_avail:
                if item not in available_start_times:
                    self.fail("Time: %s is NOT an available time, it should be available" % (item))

    #
    # NOTE: the end minute of an available default should be stored on a quanta boundary:
    #
    #   example:    start_minute: 0  end_minute: 24*60
    #
    # DO NOT store end_minute as (24*60)-1
    #


    def test_open_dates_40_seconds(self):
        """
            Performance test a query that is taking at least 40 seconds.
        """

        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60, 24)

        # this is a friday
        start_datetime = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 11, 4, 23, 59, 59)

        # we assume 2976 is the right answer
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=2976)


    def test_one_hour_query(self):
        """Test that a query for a 1-hr range performs correctly."""

        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60, 24)

        # insert an existing service - to overlap the hour in question and remove all available time
        ss = self.dh.insertScheduledService(1, datetime(2010, 6, 10, 17, 00), datetime(2010, 6, 10, 19, 00))

        # this is a friday
        start_datetime = MaintcalDatetime(2010, 6, 10, 18, 0, 0)
        end_datetime = MaintcalDatetime(2010, 6, 10, 19, 0, 0)
        
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1, result=0)


    def test_open_dates(self):
        """Test an entire day with no exceptions and no schedules.

        Possibilites for scheduling a gived service into a given period
            with no blocks and no other schedules:

        possibilities = (2*period length in hours) + 1 - length of service in quanta

        This function can be used when writing the tests
        """

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)

        # this is a friday
        start_datetime = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 9, 4, 23, 59, 59)

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=48,
                is_avail = [ datetime( 2009, 9, 4, 01, 00, 00),
                             datetime( 2009, 9, 4, 01, 00, 00), 
                             datetime( 2009, 9, 4, 23, 30, 00), 
                             datetime( 2009, 9, 4, 12, 00, 00) ],
                not_avail = [ datetime( 2009, 9, 5, 00, 00, 00) ])

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1.0, result=47)
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1.5, result=46)
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=2.0, result=45)
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=10.0, result=29)
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=20.0, result=9)
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=24.0, result=1)

    def test_calendar_no_available_time(self):
        """
            Test a calendar that has no available time. Ever. In response
            to the MSSQL DBA calendar.
        """
        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60, 0)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60, 0)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60, 0)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60, 0)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 0)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 0)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60, 0)
        
        # this is a friday
        start_datetime = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 9, 4, 23, 59, 59)
        # return 0 available time
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1.0, result=0)

    def test_break_bitmasks(self):
        """
        NOTE: the work_unit is defined as an hour.
        """

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 9*60, 0)
        self.dh.insertAvailableDefault(1, 4, 9*60, 10*60, 0.5)
        self.dh.insertAvailableDefault(1, 4, 10*60, 24*60, 0)

        # this is a friday
        start_datetime = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 9, 4, 23, 59, 59)

        # There should be no available slots for an entire hour
        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1, result=0)

    def test_cross_periods_with_overlap_services(self):
        """
            Test that there should be no available time when a service overlaps two periods.
            see 100315-05269 and 100315-03418 for details.
        """
        # Monday - 7:30 AM to 3:30 PM with 7.5 work units
        self.dh.insertAvailableDefault(1, 0, 7.5*60, 15.5*60, 7.5)
        # Monday - 3:30 PM to 12:00 AM with 7.5 work units
        self.dh.insertAvailableDefault(1, 0, 15.5*60, 24*60, 7.5)

        # insert an existing service
        self.dh.insertScheduledService(1, datetime(2009, 8, 31, 14, 30), datetime(2009, 8, 31, 16, 30))

        start_datetime = MaintcalDatetime(2009, 8, 31, 14, 0, 0)
        end_datetime = MaintcalDatetime(2009, 8, 31, 17, 0, 0)

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1, result=0)

    def test_with_simple_large_scheduled_service(self):

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)

        # saturday
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 24)

        # this is a friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_date = MaintcalDatetime(2009, 9, 4, 23, 59, 59)

        # service from 1am to 11pm
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 1, 0), datetime(2009, 9, 4, 23, 0))

        # times_available should now consider 2 different 1 hr blocks:
        # midnight to 1am, and 11pm to midnight

        # these two cases can also fit in the first period

        # 2 + 2 
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=4, 
                not_avail= [ datetime(2009,9,4,1,0,0), datetime(2009,9,4,22,30,0) ],
                is_avail= [ datetime(2009,9,4,23,0,0) ] )

        # 1 + 1
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1.0, result=2)

        # these cases cannot fit in either period

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1.5, result=0)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=2.0, result=0)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=10.0, result=0)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=20.0, result=0)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=22.0, result=0)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=24.0, result=0)


    def test_with_simple_scheduled_service_no_next_day(self):
        # We are testing a situation where the is no available time on the next day

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)

        # saturday
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 0)

        # this is a friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_date = MaintcalDatetime(2009, 9, 4, 23, 59, 59)

        # service from 1am to 2am
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 1, 0), datetime(2009, 9, 4, 2, 0))

        # times_avaiable is now within 3 different periods:
        # midnight to 1 which is a 1 hr
        # 2 to end of day which is 22 hrs
        # the next day has available time, so we can schedule all the way to midnight as a start time

        # these two cases can also fit in the first period

        # 2 + 44
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=46,
                not_avail = [ datetime( 2009, 9, 4, 1, 00, 00) ] )
        # 1 + 43
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1.0, result=44)

        # these cases cannot fit in the first period
        # therefore they can only fit in a period of 22 hrs or 44 quanta

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1.5, result=42)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=2.0, result=41)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=10.0, result=25)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=20.0, result=5)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=22.0, result=1,
            is_avail = [ datetime( 2009, 9, 4, 02, 00, 00) ] )
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=24.0, result=0)

    def test_bring_in_past_due_services(self):
        """
        Make sure that the calculator includes past due services.
        """

        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60, 24)
        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 24)

        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 5, 0), datetime(2009, 9, 4, 6, 0), state=ScheduledService.State.PAST_DUE )

        # this is a friday
        start_date = MaintcalDatetime(2009, 9, 4, 5, 0, 0)
        end_date   = MaintcalDatetime(2009, 9, 4, 6, 0, 0)

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1.0, result=0)

    def test_with_simple_scheduled_service_all_next_day(self):

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)

        # saturday
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 24)

        # this is a friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_date = MaintcalDatetime(2009, 9, 4, 23, 59, 59)

        # service from 1am to 2am
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 1, 0), datetime(2009, 9, 4, 2, 0))

        # times_available is now within 3 different periods:
        # midnight to 1 which is a 1 hr
        # 2 to end of day which is 22 hrs
        # the next day has available time, so we can schedule all the way to midnight as a start time

        # these two cases can also fit in the first period

        # 2 + 44
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=46)
        # 1 + 44
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1.0, result=44)

        # these cases cannot fit in the first period
        # therefore they can only fit in a period of 22 hrs or 44 quanta

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1.5, result=42)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=2.0, result=41)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=10.0, result=25)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=20.0, result=5)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=22.0, result=1)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=24.0, result=0)

    def test_boundary_condition(self):
        """
        Test a blocked period followed by an open on
        """

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 12*60, 12)
        self.dh.insertAvailableDefault(1, 4, 12*60, 24*60, 12)

        # saturday
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 0)

        # 12 hour service
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 0, 0), datetime(2009, 9, 4, 12, 0))

        # this is a friday
        # We will query from 11am to 1pm, which is a 2 hr window
        start_date = MaintcalDatetime(2009, 9, 4, 11, 0, 0)
        end_date = MaintcalDatetime(2009, 9, 4, 12, 59, 59)

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=2)

        # There should be 1 slot that can contain an hour
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1, result=1)


    def test_depth(self):

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 12*60, 12)
        self.dh.insertAvailableDefault(1, 4, 12*60, 24*60, 24)

        # saturday
        self.dh.insertAvailableDefault(1, 5, 0*60, 12*60, 12)
        self.dh.insertAvailableDefault(1, 5, 12*60, 24*60, 24)

        # this is friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_date = MaintcalDatetime(2009, 9, 4, 23, 59, 59)

        # service from 11am to 1pm
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 11, 0), datetime(2009, 9, 4, 13, 0))

        # because the second half of friday has a depth of two, nothing after noon should be blocked out

        # this should yield a period from midnight to 11am, and a block from noon to midnight
        # block 1 = 11 hours
        # block 2 = 12 hours

        # 22 + 24
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=46)

        # 21 + 23
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1, result=44)

        # 0 + 1 
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=12, result=1)


    def test_date_range(self):

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 12*60, 12)
        self.dh.insertAvailableDefault(1, 4, 12*60, 24*60, 24)

        # Satuday with a depth of 2 all day long
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 48)

        # service from friday 8pm to sat 4am
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 20, 0), datetime(2009, 9, 5, 4, 0))

        # This should yield 1 period for all of friday and saturday
        # this period will have a length of 48
        # because the depth of the periods should handle the scheduled service
        # without blocking out any time

        # this is friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        # this is saturday
        end_date = MaintcalDatetime(2009, 9, 5, 23, 59, 59)

        # 97 
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=96)

        return

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1, result=95)

        # 97 - 42 = 55
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=21, result=55)

    def test_broken_exception(self):

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)

        # Satuday
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 0)

        # exceptions for friday
        self.dh.insertAvailableException(1, date(2009, 9, 4), 0*60, 8*60, 1) 
        self.dh.insertAvailableException(1, date(2009, 9, 4), 8*60, 12*60, 1)
        self.dh.insertAvailableException(1, date(2009, 9, 4), 12*60, 24*60, 1)

        # this is friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        # this is saturday
        end_date = MaintcalDatetime(2009, 9, 5, 23, 59, 59)

        # 47 because saturday is done
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1, result=47)

 
    def test_date_range_with_exception(self):

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 12*60, 12)
        self.dh.insertAvailableDefault(1, 4, 12*60, 24*60, 24)

        # Satuday - all day is depth 2
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 48)

        # exceptions for saturday
        self.dh.insertAvailableException(1, date(2009, 9, 5), 0*60, 8*60, 8)        # 0-8   depth 1
        self.dh.insertAvailableException(1, date(2009, 9, 5), 8*60, 12*60, 8)       # 8-12  depth 2
        self.dh.insertAvailableException(1, date(2009, 9, 5), 12*60, 24*60, 12)     # 12-24 depth 1

        # service from friday 8pm to sat 4am
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 20, 0), datetime(2009, 9, 5, 4, 0))

        # This should yield 1 period for all of friday
        # and 1 period for saturday from 4am to midnight sunday
        # period 1 length = 24, period 2 length = 20

        # this is friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        # this is saturday
        end_date = MaintcalDatetime(2009, 9, 5, 23, 59, 59)

        # 48 + 40
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=88)

        # 47 + 39
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1, result=86)

        # friday: ( 48 slots + 1 ) - 21 * 2 = 49 - 42 = 7
        # saturday: 0 slots
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=21, result=7)

    def test_max_out_time(self):

        # This tests maxing out a period

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 8*60, 0)
        self.dh.insertAvailableDefault(1, 4, 8*60, 10*60, 1)   # 1 hr in a 2 hr period
        self.dh.insertAvailableDefault(1, 4, 10*60, 24*60, 0)

        # service from friday 8am to 9am
        # This service should suck up all available time
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 8, 0), datetime(2009, 9, 4, 9, 0))

        # this is friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_date = MaintcalDatetime(2009, 9, 4, 23, 59, 0)

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=0)


    def test_use_up_depth_of_three(self):

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 12*60, 24)  # depth of 2
        self.dh.insertAvailableDefault(1, 4, 12*60, 24*60, 36)  # depth of 3

        # saturday
        self.dh.insertAvailableDefault(1, 5, 0*60, 12*60, 12)
        self.dh.insertAvailableDefault(1, 5, 12*60, 24*60, 24)

        # 10am to 2pm
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 10, 0), datetime(2009, 9, 4, 14, 0))

        # 11am to 2pm
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 11, 0), datetime(2009, 9, 4, 14, 0))

        # 1pm to 4pm
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 13, 0), datetime(2009, 9, 4, 16, 0))

        # this will give 1 period from midnight to 11am
        # from 11am to noon is blocked
        # from noon to 1pm is open
        # from 1pm to 2pm is blocked
        # from 2pm to midnight is open

        # 3 periods are open:
        # midnight to 11am    11 hrs
        # noon to 1pm          1 hr
        # 2pm to midnight     10 hr

        # this is friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_date = MaintcalDatetime(2009, 9, 4, 23, 59, 59)

        # 22 + 2 + 20
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=44)

        # 21 + 1 + 19 
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1, result=41)

        # 20 + 0 + 18
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=1.5, result=38)

        # 3 + 0 + 1 
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=10, result=4)

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=11, result=1)

    def test_when_day_is_full(self):

        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 12)

        # this is a friday
        start_date = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_date = MaintcalDatetime(2009, 9, 4, 23, 59, 59)

        # service for all day 
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 0, 0), datetime(2009, 9, 4, 23, 59))

        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=0.5, result=0)
        self.assertTimesAvailable(start_date=start_date, end_date=end_date, svc_len=24, result=0)





    def BAD_needs_more_defaults_test_overlap_scheduled_now(self):
        """ 
            service should not overlap one another. 
        """
        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24) # all day depth of 1. 

        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 10, 0), datetime(2009, 9, 4, 13, 0))

        # this is a friday
        start_datetime = MaintcalDatetime(2009, 9, 1, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 9, 30, 0, 0, 0)

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1.5, result=1,
                not_avail = [ datetime( 2009, 9, 4, 10, 00, 00 ) ] )

    def test_query_boundries(self):
        
        # Friday
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)

        # this is a friday
        start_datetime = MaintcalDatetime(2009, 9, 4, 22, 0, 0)
        end_datetime = MaintcalDatetime(2009, 9, 4, 23, 00, 00)

        # Times available should never return times that could extend outside of our requested range.
        # Example: if 10:00 - 12:00 is avail, and we ask for times avail from 10:00 to 11:00 
        # we should get only 1 avail time, which is 10:00
        self.dh.insertScheduledService(1, datetime(2009, 9, 4, 0, 0), datetime(2009, 9, 4, 22, 0))

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1.0, result=1,
                is_avail = [ datetime( 2009, 9, 4, 22, 00, 00 ) ] )

    def test_corner_case_nov_utc_defaults(self):
        """
        Query across the nov 1 switch.

This is the 'ambiguous hour'

    ryan.springer@d-db1:~$ zdump -v US/Central | grep 2009 | grep Nov
    US/Central  Sun Nov  1 06:59:59 2009 UTC = Sun Nov  1 01:59:59 2009 CDT isdst=1 gmtoff=-18000
    US/Central  Sun Nov  1 07:00:00 2009 UTC = Sun Nov  1 01:00:00 2009 CST isdst=0 gmtoff=-21600

    If the client sends us 1:30 US/Central, this is an ambiguous datetime.

        """
        # Sunday
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60, 24)

        # this is a sunday
        start_datetime = MaintcalDatetime(2009, 11, 1, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 11, 1, 23, 59, 0)

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=48,
                calendar_ids = [1],
                is_avail = [ datetime( 2009, 11, 1, 00, 00, 00 ), datetime( 2009, 11, 1, 00, 00, 00 ) ] )


    def test_corner_case_nov_non_utc_defaults(self):
        """
        """
        # Saturday
        self.dh.insertAvailableDefault(2, 5, 0*60, 24*60, 24)
        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)
        # Monday
        self.dh.insertAvailableDefault(2, 0, 0*60, 24*60, 24)

        # this is a utc sunday
        start_datetime = MaintcalDatetime(2009, 11, 1, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 11, 1, 23, 59, 0)

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=48,
                calendar_ids = [2],
                is_avail = [ datetime( 2009, 11, 1, 00, 00, 00 ), datetime( 2009, 11, 1, 00, 00, 00 ) ] )

    def test_corner_case_nov_with_exceptions(self):
        self.broken_test() ; return

        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)

        # this is a sunday
        start_datetime = MaintcalDatetime(2009, 11, 1, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 11, 1, 23, 00, 00)

        # Insert some exceptions
        self.dh.insertAvailableException(1, date(2009, 11, 1), 0*60, 8*60, 9) # Un-even Depth
        self.dh.insertAvailableException(1, date(2009, 11, 1), 8*60, 12*60, 8)

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=49 )
                #is_avail = [ datetime( 2009, 9, 4, 22, 00, 00 ) ] )

    def test_corner_case_nov_with_schedules(self):
        self.broken_test() ; return

        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)

        # this is a sunday
        start_datetime = MaintcalDatetime(2009, 11, 1, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 11, 1, 23, 00, 00)

        # service from 1am to 2am
        self.dh.insertScheduledService(1, datetime(2009, 11, 1, 1, 0), datetime(2009, 11, 1, 3, 0))

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=46 )
                #is_avail = [ datetime( 2009, 9, 4, 22, 00, 00 ) ] )

    def test_corner_case_nov_with_schedules_and_exceptions(self):
        self.broken_test() ; return

        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)

        # this is a sunday
        start_datetime = MaintcalDatetime(2009, 11, 1, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 11, 1, 23, 00, 00)

        # Insert some exceptions
        self.dh.insertAvailableException(1, date(2009, 11, 1), 0*60, 8*60, 9) # Un-even Depth
        self.dh.insertAvailableException(1, date(2009, 11, 1), 8*60, 12*60, 8)

        # service from 1am to 2am
        self.dh.insertScheduledService(1, datetime(2009, 11, 1, 1, 0), datetime(2009, 11, 1, 3, 0))

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=47 )
                #is_avail = [ datetime( 2009, 9, 4, 22, 00, 00 ) ] )


    def test_corner_case_mar(self):
        """

This tests the non-existent hour

    ryan.springer@d-db1:~$ zdump -v US/Central | grep 2009 | grep Mar
    US/Central  Sun Mar  8 07:59:59 2009 UTC = Sun Mar  8 01:59:59 2009 CST isdst=0 gmtoff=-21600
    US/Central  Sun Mar  8 08:00:00 2009 UTC = Sun Mar  8 03:00:00 2009 CDT isdst=1 gmtoff=-18000

    If the client sends us 2:30 US/Central, this is not a validate datetime.

        """

        # Saturday
        self.dh.insertAvailableDefault(2, 5, 0*60, 24*60, 24)
        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)
        # Monday
        self.dh.insertAvailableDefault(2, 0, 0*60, 24*60, 24)

        # this is a utc sunday
        start_datetime = MaintcalDatetime(2009, 3, 8, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 3, 8, 23, 59, 00)


        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=48,
                calendar_ids = [2])

        #        is_avail = [ datetime( 2009, 11, 1, 00, 00, 00 ), datetime( 2009, 11, 1, 00, 00, 00 ) ] )


    def test_corner_case_mar_with_exceptions(self):
        self.broken_test() ; return

        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)

        # this is a sunday
        start_datetime = MaintcalDatetime(2009, 3, 8, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 3, 8, 23, 00, 00)

        # Insert some exceptions
        self.dh.insertAvailableException(2, date(2009, 3, 8), 0*60, 8*60, 9) # Un-even Depth
        self.dh.insertAvailableException(2, date(2009, 3, 8), 8*60, 12*60, 8)

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=49 )
                #is_avail = [ datetime( 2009, 9, 4, 22, 00, 00 ) ] )

    def test_corner_case_nov_with_schedules(self):
        self.broken_test() ; return

        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)

        # this is a sunday
        start_datetime = MaintcalDatetime(2009, 3, 8, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 3, 8, 23, 00, 00)

        # service from 1am to 2am
        self.dh.insertScheduledService(1, datetime(2009, 3, 8, 1, 0), datetime(2009, 11, 1, 3, 0))

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=46 )
                #is_avail = [ datetime( 2009, 9, 4, 22, 00, 00 ) ] )

    def test_corner_case_nov_with_schedules_and_exceptions(self):
        self.broken_test() ; return

        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)

        # this is a sunday
        start_datetime = MaintcalDatetime(2009, 3, 8, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 3, 8, 23, 00, 00)

        # Insert some exceptions
        self.dh.insertAvailableException(1, date(2009, 3, 8), 0*60, 8*60, 9) # Un-even Depth
        self.dh.insertAvailableException(1, date(2009, 3, 8), 8*60, 12*60, 8)

        # service from 1am to 2am
        self.dh.insertScheduledService(1, datetime(2009, 3, 8, 1, 0), datetime(2009, 11, 1, 3, 0))

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=47 )
                #is_avail = [ datetime( 2009, 9, 4, 22, 00, 00 ) ] )

    def test_multi_calendar_open_dates(self):

        # Thursday
        self.dh.insertAvailableDefault(2, 3, 0*60, 24*60, 0)
        self.dh.insertAvailableDefault(3, 3, 0*60, 24*60, 0)

        # Friday

        # This will give us one overlapping hour, because cal 2 is central and cal 3 is eastern
        # which is between hour 17 and hour 18 in UTC

        self.dh.insertAvailableDefault(2, 4, 0*60, 12*60, 0)
        self.dh.insertAvailableDefault(2, 4, 12*60, 14*60, 2)
        self.dh.insertAvailableDefault(2, 4, 14*60, 24*60, 0)

        self.dh.insertAvailableDefault(3, 4, 0*60, 12*60, 0)
        self.dh.insertAvailableDefault(3, 4, 12*60, 14*60, 2)
        self.dh.insertAvailableDefault(3, 4, 14*60, 24*60, 0)

        # Saturday
        self.dh.insertAvailableDefault(2, 5, 0*60, 24*60, 0)
        self.dh.insertAvailableDefault(3, 5, 0*60, 24*60, 0)

        # this is a friday
        start_datetime = MaintcalDatetime(2009, 9, 4, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 9, 4, 23, 59, 0)

        # print MaintcalDatetime(2009, 9, 4, 17, 0, 0).to_python_datetime('America/Chicago')
        # This is 12 o clock central and 1 o clock eastern, which is valid in both calendars

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=2,
                is_avail = [ datetime( 2009, 9, 4, 17, 00, 00),
                             datetime( 2009, 9, 4, 17, 30, 00) ],
                not_avail = [ datetime( 2009, 9, 5, 00, 00, 00) ], calendar_ids = [2, 3])

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1.0, result=1, 
                is_avail = [ datetime( 2009, 9, 4, 17, 00, 00) ],
                calendar_ids = [2, 3] )

    def test_calendar_should_not_allow_overbooking(self):
        """
        This problem was discovered where the system allows overbooking
        """

        # Friday
        self.dh.insertAvailableDefault(2, 4, 0*60, 24*60, 24)
        # Saturday
        self.dh.insertAvailableDefault(2, 5, 0*60, 24*60, 24)
        # Sunday
        self.dh.insertAvailableDefault(2, 6, 0*60, 24*60, 24)
        # Monday
        self.dh.insertAvailableDefault(2, 0, 0*60, 24*60, 24)


        # service from 8am to 8:30am
        self.dh.insertScheduledService(2, datetime(2009, 12, 12, 8, 0), datetime(2009, 12, 12, 8, 30))

        # this is an overbooked service from 8am to 10am
        self.dh.insertScheduledService(2, datetime(2009, 12, 12, 8, 0), datetime(2009, 12, 12, 10, 0))

        # this is a saturday
        start_datetime = MaintcalDatetime(2009, 12, 12, 0, 0, 0)
        end_datetime = MaintcalDatetime(2009, 12, 12, 23, 59, 0)

        # midnight-8:
        #
        #   can start at 12:00, 12:30 ... all the way up to and including 7
        #   12, 1, 2, 3, 4, 5, 6 hours + at 7 = 2 * 7 + 1 = 14 + 1 = 15  

        # 10- midnight
        #
        #   can start at 10, 10:30 ... all the way up to and including 11:00
        #   10, 11, 12
        #   1, 2,  3   4
        #   5  6   7   8
        #   9  10  
        #        and 11

        # 10 - midnight = 14 hours = 28 - 1 = 27 slots

        # 15 + 27 = 42

        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=1, result=42,
                is_avail = [ datetime( 2009, 12, 12, 17, 00, 00),
                             datetime( 2009, 12, 12, 17, 30, 00) ],
                not_avail = [ datetime( 2009, 9, 5, 00, 00, 00) ], calendar_ids = [2])

    def do_not_test_calendar_iad_overbooking(self):
        """
        This is trying to recreate the iad overbooking situation reported around may 11, 2010.

        NOTE: CALENDAR 1 in the test data is set to UTC
        NOTE: CALENDAR 2 in the test data is set to America/Chicago
        NOTE: CALENDAR 3 in the test data is set to America/New York


        It was for calendar 23 - DC ops (IAD2) which is america/new york

core_dev=> select id, start_time, end_time, state_id, date_assigned from mcal.scheduled_service where start_time < '2010-05-13' and end_time > '2010-05-11' and calendar_id = 23  order by start_time;
   id   |     start_time      |      end_time       | state_id |       date_assigned        
--------+---------------------+---------------------+----------+----------------------------
 187550 | 2010-05-11 00:00:00 | 2010-05-11 01:00:00 |        5 | 2010-05-10 17:45:40.831042
 187553 | 2010-05-11 01:00:00 | 2010-05-11 02:00:00 |        5 | 2010-05-10 17:56:24.415255
 187267 | 2010-05-11 03:00:00 | 2010-05-11 03:30:00 |        5 | 2010-05-10 08:13:33.903963
 187047 | 2010-05-11 04:30:00 | 2010-05-11 07:30:00 |        6 | 2010-05-07 16:16:45.929575      107991 = scheduled maintenance id
 187366 | 2010-05-11 07:30:00 | 2010-05-11 08:00:00 |        4 | 2010-05-10 11:37:24.440085
 187278 | 2010-05-11 08:00:00 | 2010-05-11 09:00:00 |        2 | 2010-05-10 08:26:07.635548
 187404 | 2010-05-11 09:00:00 | 2010-05-11 09:30:00 |        2 | 2010-05-10 13:11:19.03916
 187568 | 2010-05-11 10:00:00 | 2010-05-11 11:00:00 |        2 | 2010-05-10 18:13:13.072803
 187500 | 2010-05-11 17:30:00 | 2010-05-11 22:00:00 |        2 | 2010-05-10 16:12:20.530893      108270 = scheduled maintenance id - This one should have not been booked
 187359 | 2010-05-11 22:30:00 | 2010-05-11 23:00:00 |        4 | 2010-05-10 11:25:57.49938
 187547 | 2010-05-12 05:30:00 | 2010-05-12 06:00:00 |        2 | 2010-05-10 17:28:16.340767
 187561 | 2010-05-12 09:30:00 | 2010-05-12 10:30:00 |        4 | 2010-05-10 18:01:08.731342
(12 rows)


class ScheduledService(MaintcalModel):
    class State(object):
        TENTATIVE = 1
        SCHEDULED = 2
        CANCELED = 4
        COMPLETED = 5
        PAST_DUE = 6


We have a pair of maintenances that won't respect each other's personal
space:

100510-12062 Rekick on 2 servers 1:30 to 6:00 today

    maintenance_id = 108270

    100510-12063 start may 11 12:30 pm Cdt
                       may 11  5:00 pm Cdt

and

    100511-05488 RAM Upgrade for two servers 2:30 to 3:30 today

    maintenance_id = 108451

        start 2:30 or 14:30 EDT, which is 18:30 UTC
        end   3:30 or 15:30 EDT, which is 19:30 UTC


   id   | master_ticket | account_id | account_name | state_id |       date_assigned        | additional_duration | expedite |                general_description                | service_type_id | contact_id |       creation_date        |     modification_date      
--------+---------------+------------+--------------+----------+----------------------------+---------------------+----------+---------------------------------------------------+-----------------+------------+----------------------------+----------------------------
 108451 | 100511-04026  |     933305 | Agency Q     |        5 | 2010-05-11 12:54:51.387365 | 00:30:00            | f        | 32GB of RAM for each server in maintenance bin Z0 |              21 |     513598 | 2010-05-11 12:54:51.387365 | 2010-05-11 14:22:02.998173
(1 row)




core_dev=> select dow, start_minutes, end_minutes, work_units_in_quanta from mcal.available_defaults where calendar_id=23 order by dow, start_minutes;
 dow | start_minutes | end_minutes | work_units_in_quanta 
-----+---------------+-------------+----------------------
   0 |             0 |         420 |                   14
   0 |           420 |         480 |                    0
   0 |           480 |         600 |                    4
   0 |           600 |         720 |                    0
   0 |           720 |         900 |                    6
   0 |           900 |         960 |                    0
   0 |           960 |        1380 |                   14
   0 |          1380 |        1440 |                    0
   1 |             0 |         420 |                   14
   1 |           420 |         480 |                    0
   1 |           480 |         900 |                   14
   1 |           900 |         960 |                    0
   1 |           960 |        1380 |                   14
   1 |          1380 |        1440 |                    0
   2 |             0 |         420 |                   14
   2 |           420 |         480 |                    0
   2 |           480 |         900 |                   14
   2 |           900 |         960 |                    0
   2 |           960 |        1380 |                   14
   2 |          1380 |        1440 |                    0
   3 |             0 |         420 |                   14
   3 |           420 |         480 |                    0
   3 |           480 |         900 |                   14
   3 |           900 |         960 |                    0
   3 |           960 |        1380 |                   14
   3 |          1380 |        1440 |                    0
   4 |             0 |         420 |                   14
   4 |           420 |         480 |                    0
   4 |           480 |         900 |                   14
   4 |           900 |         960 |                    0
   4 |           960 |        1380 |                   14
   4 |          1380 |        1440 |                    0
   5 |             0 |         420 |                   14
   5 |           420 |         480 |                    0
   5 |           480 |         900 |                   14
   5 |           900 |         960 |                    0
   5 |           960 |        1380 |                   14
   5 |          1380 |        1440 |                    0
   6 |             0 |         420 |                   14
   6 |           420 |         480 |                    0
   6 |           480 |         900 |                   14
   6 |           900 |         960 |                    0
   6 |           960 |        1380 |                   14
   6 |          1380 |        1440 |                    0

        """

        # 0 = monday
        self.dh.insertAvailableDefault(3, 0, 0,     420,  7)
        self.dh.insertAvailableDefault(3, 0, 420,   480,  0)
        self.dh.insertAvailableDefault(3, 0, 480,   600,  2)
        self.dh.insertAvailableDefault(3, 0, 600,   720,  0)
        self.dh.insertAvailableDefault(3, 0, 720,   900,  3)
        self.dh.insertAvailableDefault(3, 0, 900,   960,  0)
        self.dh.insertAvailableDefault(3, 0, 960,   1380, 7)
        self.dh.insertAvailableDefault(3, 0, 1380,  1440, 0)

        # 1 = tuesday
        self.dh.insertAvailableDefault(3, 1, 0,     420,  7)
        self.dh.insertAvailableDefault(3, 1, 420,   480,  0)
        self.dh.insertAvailableDefault(3, 1, 480,   900,  7)
        self.dh.insertAvailableDefault(3, 1, 900,   960,  0)
        self.dh.insertAvailableDefault(3, 1, 960,   1380, 7)
        self.dh.insertAvailableDefault(3, 1, 1380,  1440, 0)

        # 2 = wed
        self.dh.insertAvailableDefault(3, 2, 0,     420,  7)
        self.dh.insertAvailableDefault(3, 2, 420,   480,  0)
        self.dh.insertAvailableDefault(3, 2, 480,   900,  7)
        self.dh.insertAvailableDefault(3, 2, 900,   960,  0)
        self.dh.insertAvailableDefault(3, 2, 960,   1380, 7)
        self.dh.insertAvailableDefault(3, 2, 1380,  1440, 0)


        """
core_dev=> select * from mcal.available_exceptions where calendar_id=23 and exception_date='2010-05-11';
  id   | calendar_id | exception_date | start_minutes | end_minutes | work_units_in_quanta |   comments   |       creation_date        |     modification_date      
-------+-------------+----------------+---------------+-------------+----------------------+--------------+----------------------------+----------------------------
 26390 |          23 | 2010-05-11     |             0 |         450 |                   14 | 3rd Shift    | 2010-05-04 10:02:43.553377 | 2010-05-04 10:02:43.553377
 26391 |          23 | 2010-05-11     |           450 |         600 |                   14 | 1st Shift    | 2010-05-04 10:02:43.553377 | 2010-05-04 10:02:43.553377
 26392 |          23 | 2010-05-11     |           600 |         810 |                    0 | JACQUES TALK | 2010-05-04 10:02:43.553377 | 2010-05-04 10:02:43.553377
 26393 |          23 | 2010-05-11     |           810 |         930 |                    4 |              | 2010-05-04 10:02:43.553377 | 2010-05-04 10:02:43.553377
 26394 |          23 | 2010-05-11     |           930 |        1440 |                   14 | 2nd Shift    | 2010-05-04 10:02:43.553377 | 2010-05-04 10:02:43.553377
(5 rows)

        """

        # This is taken from core_dev
        # These are in IAD2 time

        # These shouldn't affect the outcome
        self.dh.insertAvailableException(3, date(2010, 5, 10), 0,    450,   7 )
        self.dh.insertAvailableException(3, date(2010, 5, 10), 450,  630,   0 )
        self.dh.insertAvailableException(3, date(2010, 5, 10), 630,  900,   3 )
        self.dh.insertAvailableException(3, date(2010, 5, 10), 900,  1080,  0 )
        self.dh.insertAvailableException(3, date(2010, 5, 10), 1080, 1440,  5 )

        # These 5 exceptions created at 2010-05-04 10:02:43
        self.dh.insertAvailableException(3, date(2010, 5, 11), 0,    450,   7 ) 
        self.dh.insertAvailableException(3, date(2010, 5, 11), 450,  600,   7 )
        self.dh.insertAvailableException(3, date(2010, 5, 11), 600,  810,   0 )
        self.dh.insertAvailableException(3, date(2010, 5, 11), 810,  930,   2 )
        self.dh.insertAvailableException(3, date(2010, 5, 11), 930,  1440,  7 )

        # only the first bucket should affect the outcome

        self.dh.insertAvailableException(3, date(2010, 5, 12), 0,    450,   7 )
        self.dh.insertAvailableException(3, date(2010, 5, 12), 450,  930,   7 )
        self.dh.insertAvailableException(3, date(2010, 5, 12), 930,  1440,  7 )

        """
        This is the predicted EDT day of may 11:

        self.dh.insertAvailableException(2, date(2010, 5, 11), 0,    450,   7 )   12     7:30
        self.dh.insertAvailableException(2, date(2010, 5, 11), 450,  600,   7 )   7:30  10:00
        self.dh.insertAvailableException(2, date(2010, 5, 11), 600,  810,   0 )  10:00  13:30
        self.dh.insertAvailableException(2, date(2010, 5, 11), 810,  930,   2 )  13:30  15:30
        self.dh.insertAvailableException(2, date(2010, 5, 11), 930,  1440,  7 )  15;30  24:00

        self.dh.insertAvailableException(2, date(2010, 5, 12), 0,    450,   7 )   00:00  7:30

        converted to UTC

        4am     11:30       14 quanta
        11:30   14:00       14
        14:00   17:30       0
        17:30   19:30       4
        19:30   04:00       14

        """


        # this is a Tuesday EDT
        start_datetime = MaintcalDatetime( 2010, 5, 11,  4,  0, 0 )
        end_datetime   = MaintcalDatetime( 2010, 5, 12,  3, 59, 0 )


        """
 187278 | 2010-05-11 08:00:00 | 2010-05-11 09:00:00 |        2 | 2010-05-10 08:26:07.635548
 187404 | 2010-05-11 09:00:00 | 2010-05-11 09:30:00 |        2 | 2010-05-10 13:11:19.03916
 187568 | 2010-05-11 10:00:00 | 2010-05-11 11:00:00 |        2 | 2010-05-10 18:13:13.072803
 187500 | 2010-05-11 17:30:00 | 2010-05-11 22:00:00 |        2 | 2010-05-10 16:12:20.530893
 187547 | 2010-05-12 05:30:00 | 2010-05-12 06:00:00 |        2 | 2010-05-10 17:28:16.340767
        """

        # These times are in UTC, which is 4 hrs ahead of EDT 

        self.dh.insertScheduledService(3, datetime(2010, 5, 11, 8, 0),   datetime(2010, 5, 11, 9, 0))   
        self.dh.insertScheduledService(3, datetime(2010, 5, 11, 9, 0),   datetime(2010, 5, 11, 9, 30))  
        self.dh.insertScheduledService(3, datetime(2010, 5, 11, 10, 0),  datetime(2010, 5, 11, 11, 0))  

        # maintenance 108270 from 12:30 to 5:00 CDT, which is 13:30 - 18:00 EDT
        #            which is 17:30 to 22:00 UTC
        self.dh.insertScheduledService(3, datetime(2010, 5, 11, 17, 30), datetime(2010, 5, 11, 22, 0)) 

        self.dh.insertScheduledService(3, datetime(2010, 5, 12, 5, 30),  datetime(2010, 5, 12, 6, 0)) 

        # 

        """
        UTC orignal buckets

        4am     11:30       14 quanta
            8-9    taken, remove 2 quanta
            9-9:30 taken, remove 0.5 quanta
            10-11  taken, remove 2 quanta
            remove 2.5 hours, leave 5 hours = 10 possible quanta
            9.5 quanta left

        11:30   14:00       14
            2.5 hours left = 5 quanta 
        14:00   17:30       0
        17:30   19:30       4
            4 quanta taken, 0 left
        19:30   04:00       14
            5 quanta taken, 9 quanta left
            22:00 - 28:00 = 6 hours left with possible 9 quanta
            12 quanta possible

        10 + 5 + 12 = 27
        """


        """
    100511-05488 RAM Upgrade for two servers 2:30 to 3:30 today

    maintenance_id = 108451

        start 1:30 CDT which is 13:30 CDT

        which is 

        14:30 EDT

        which is

        18:30 UTC 

        start 2:30 or 14:30 EDT, which is 18:30 UTC
        end   3:30 or 15:30 EDT, which is 19:30 UTC

        """


        self.assertTimesAvailable(start_date=start_datetime, end_date=end_datetime, svc_len=0.5, result=27, 
                not_avail = [ datetime( 2010, 5, 11, 18, 30, 00) ], calendar_ids = [3])

