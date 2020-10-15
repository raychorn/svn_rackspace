"""
    The calculator fuzzer!

This is inherently the same as recreating the calendar....


Type signatures ( in haskellish format ):

    calculator :: available_time_db_records -> query -> available_times

    available_time_db_records :: [available_default] -> [available_exception] -> [scheduled_service]

    query :: start_datetime -> end_datetme -> service_length -> [calendar_id]

    available_times :: [start_datetime]


How to fuzz em all:

"""
from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib.times_available.calculator import Calculator
from maintcal.lib.times_available.times_available_query import TimesAvailableQuery
from maintcal.model import db_sess, ScheduledService, AvailableDefaults, AvailableExceptions
from datetime import datetime, date, timedelta
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime

from random import randrange

class FuzzyDefault(object):
    """
    Simple object to aid in validation.
    """
    def __init__(self, dow, start_min, end_min, wunits, length_in_quanta):
        self.dow = dow
        self.start_min = start_min
        self.end_min = end_min
        self.wunits = wunits
        self.length_in_quanta = length_in_quanta

    def __str__(self):
        out = " dow: %s" % self.dow
        out += " start_min: %s" % self.start_min
        out += " end_min: %s" % self.end_min
        out += " wunits: %s" % self.wunits
        out += " length_in_quanta: %s" % self.length_in_quanta
        return out



class FuzzyPeriod(object):
    """

    """
    @classmethod
    def from_default(cls, current_date, default):
        start_time = current_date + timedelta(minutes=default.start_min)
        end_time = current_date + timedelta(minutes=default.end_min)
        return FuzzyPeriod(start_time, end_time, default.wunits, default.length_in_quanta)

    def __init__(self, start_time, end_time, wunits, length_in_quanta):
        self.start_time = start_time
        self.end_time = end_time
        self.wunits = wunits
        self.length_in_quanta = length_in_quanta

    def possible_slots(self, service_length):
        """
        # If everything is totally open:
        """
        results = ( self.length_in_quanta + 1 ) - service_length
        return results 




class CalculatorFuzzer(object):
    """
        This class produces all of the fuzzy data
    """

    def __init__(self, dh):
        self.dh = dh

    def generate_fuzzy_data(self):
        """
        Generate some fuzzy stuff
        """
        self._query = {}
        self._defaults = {}
        self._exceptions = [] 
        self._services = []
        self._periods = []
        self._results = {}

        self._generate_query()
        self._generate_defaults()
        #self._generate_exceptions()
        #self._generate_scheduled_services()
        self._generate_results()

        return (self._query, self._defaults, self._exceptions, self._services, self._results)

    def _generate_query(self):
        """
    query

        start_datetime
            Generate a random datetime, on a quanta boundary
        end_datetime
            Add a random number of quanta to start_datetime
        service_length
            random number between 1 and 24
        """
        #
        #   Generate start datetime
        #

        # randrange is [ ), so we have to add one to the end
        self._start_year = randrange(2009, 2010 + 1)
        self._start_month = randrange(11, 12 + 1)

        # not worried about 29, 30, and 31 yet
        self._start_day = randrange(1, 28 + 1)
        self._start_hour = randrange(0, 23 + 1)

        self._start_minute = 0
        if randrange(0, 1 + 1):
            self._start_minute = 30

        self._query['start_datetime'] = datetime(self._start_year, self._start_month, self._start_day,
            self._start_hour, self._start_minute, 0)

        #   Generate end datetime

        self._query['range_in_quanta'] = randrange(4, 10 + 1)

        self._query['end_datetime'] = self._query['start_datetime'] + timedelta(minutes=30 * self._query['range_in_quanta'])

        self._query['service_length_in_quanta'] = randrange(1, 4 + 1)

        self._query['service_length'] = float(self._query['service_length_in_quanta']) / 2

        #   Cal ids

        self._query['calendar_ids'] = [1]

        print self._query

    def _generate_defaults(self):
        """
        for each default
            start min
            end min
            wunit
        """
        # Generate the defaults for each day of the week, 0 through 7
        for dow in xrange(7):
            self._defaults[dow] = []

            out = "dow: %s " % dow
            current_quanta = 0
            last_quanta = 48 # this is actually minute 1440

            while current_quanta < last_quanta:
                start_min = current_quanta * 30

                # determine how many quanta to add
                # quanta_left_in_day = last_quanta - current_quanta

                quanta_to_add = randrange(1, (last_quanta - current_quanta) + 1)
                current_quanta = current_quanta + quanta_to_add

                end_min = start_min + (quanta_to_add * 30)
                wunits = randrange(0, 10 + 1)
            
                new_default = FuzzyDefault(dow, start_min, end_min, wunits, quanta_to_add)
                self._defaults[dow].append(new_default)
                out = out + str(new_default)
                self.dh.insertAvailableDefault(1, dow, start_min, end_min, wunits)
            print out

        # Instance some fuzzy periods

        current_date = self._query['start_datetime'].date()
        end_date = self._query['end_datetime'].date()
        while current_date <= end_date:
            for d in self._defaults[current_date.weekday()]:
                self._periods.append(FuzzyPeriod.from_default(current_date, d))
            current_date = current_date + timedelta(hours=24)


        # print self._defaults


                #print "quanta left: %s  quanta to add: %s" % (quanta_left_in_day, quanta_to_add)




        """
            current_min = 0
            quanta_left_in_day = 48
            while current_min < 1440:
                if quanta_left_in_day == 1:
                    quanta_to_add = 1
                else:
                    quanta_to_add = randrange(1, quanta_left_in_day + 1)

                print "quanta left: %s  quanta to add: %s" % (quanta_left_in_day, quanta_to_add)
                quanta_left_in_day = quanta_left_in_day - quanta_to_add

                start_min = current_min
                end_min = start_min + (quanta_to_add * 30)
                wunits = randrange(0, 10 + 1)
            
                new_default = (dow, start_min, end_min, wunits)
                self._defaults.append(new_default)
                print new_default
                self.dh.insertAvailableDefault(1, dow, start_min, end_min, wunits)

                current_min = end_min

        # print self._defaults
        """


    def _generate_exceptions(self):
        """
        for each exception
            date
            start min
            end min
            wunit
        """
        print 'EXCEPTIONS: '

        current_date = self._query['start_datetime'].date()
        end_date = self._query['end_datetime'].date()
        while current_date <= end_date:
            # 50% chance of generating an exception for any given day
            if randrange(0, 1 + 1):

                current_quanta = 0
                last_quanta = 48 # this is actually minute 1440

                while current_quanta < last_quanta:
                    start_min = current_quanta * 30

                    # determine how many quanta to add
                    # quanta_left_in_day = last_quanta - current_quanta

                    quanta_to_add = randrange(1, (last_quanta - current_quanta) + 1)
                    current_quanta = current_quanta + quanta_to_add

                    end_min = start_min + (quanta_to_add * 30)
                    wunits = randrange(0, 10 + 1)
                
                    new_exception = (current_date, start_min, end_min, wunits)
                    self._exceptions.append(new_exception)
                    print new_exception
                    self.dh.insertAvailableException(1, current_date, start_min, end_min, wunits)

            current_date = current_date + timedelta(hours=24)

    def _generate_scheduled_services(self):
        """
        for each service:
            start time
            end time
        """
        print "Scheduled Services: "
        if randrange(0, 1 + 1):
            starting_quanta = randrange(0, (self._query['range_in_quanta'] - 1) + 1)
            ending_quanta = randrange(starting_quanta, (self._query['range_in_quanta'] - 1) + 1)
            
            start_time = self._query['start_datetime'] + timedelta(minutes=30 * starting_quanta)
            end_time = self._query['start_datetime'] + timedelta(minutes=30 * ending_quanta)

            new_service = (start_time, end_time)
            self._services.append(new_service)
            print new_service
            self.dh.insertScheduledService(1, start_time, end_time)
 
    def _generate_results(self):
        """
        For each open slot:

            results = ( length_of_slot_in_quanta + 1 ) - length_of_service_in_quanta

        """
        results = 0
        service_length = self._query['service_length_in_quanta']

        for p in self._periods:
            results += p.possible_slots(service_length)

        self._results['result'] = results

class TestCalculatorFuzzer(MaintcalUnitTest):

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

    def assertFuzz(self, fuzz_data):
        (query, defaults, exceptions, services, results) = fuzz_data

        self.assertTimesAvailable(
            MaintcalDatetime.from_python_datetime(query['start_datetime']),
            MaintcalDatetime.from_python_datetime(query['end_datetime']),
            query['service_length'],
            results['result'],
            calendar_ids = query['calendar_ids'])

    def assertTimesAvailable(self, start_date, end_date, svc_len, result, not_avail = False, is_avail = False, calendar_ids = [1]):
        # NOTE: seconds in the end time are currently ignored

        calculator = Calculator()
        svc_len = float(svc_len)

        query = TimesAvailableQuery(start_date, end_date, svc_len)
        available_start_times = calculator._perform_times_available_query(query, calendar_ids)
        #print 'Avail Times: ', available_start_times

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

    def disabled_test_fuzz(self):
        """
            Perform a fuzz test on the calculator
        """
        f = CalculatorFuzzer(self.dh)
        for x in xrange(1):
            self.assertFuzz(f.generate_fuzzy_data())

