from maintcal.lib.times_available import AVAIL_BIT, UNAVAIL_BIT 
from maintcal.lib.times_available import granularity_in_minutes 

from maintcal.lib.date import date_to_datetime, timedelta_to_total_seconds
import math
from datetime import timedelta

from maintcal.lib.date.timezone_normalizer import TimezoneNormalizer

class Period(object):
    """ 
        A Period is an arbitrary length of time in which an arbitrary number of "work units" can be done.

        A Period is defined by a date, a start and end minute, and a work_unit amount.
        NOTE: start_min and end_min are absolute minutes from the start of the day.



        The period will be shifted so that it will contain a UTC start and a UTC end.



        For example, if the calendar admin configures this date to do 4 units of work 
        between 10am and noon, and 10 units between noon and 6pm, this would define two periods:
            1: 10:00 - 12:00
            2: 12:00 - 18:00


        NOTE: Periods have a mutable state.
    """

    def __init__(self, current_date, start_min, end_min, work_units_in_quanta):

        self.start_min = start_min
        self.end_min = end_min
        self.work_units_in_quanta = work_units_in_quanta

        self._calculateStartAndEndTimes(current_date)
        self._calculateDurationInQuanta()
        self._calculateDepth()


    def _calculateStartAndEndTimes(self, current_date):
        """ 
            Calculate the start and end times by adding the minutes offset to the date being processed. 
        
            Note: these are localized
        """
        current_datetime = date_to_datetime(current_date)
        self.start_time = current_datetime + timedelta(minutes=self.start_min)
        self.end_time = current_datetime + timedelta(minutes=self.end_min)


    def isFull(self):
        """Has all the available time from the period been used up?"""
        return self.work_units_in_quanta <= 0


    def normalize_from_timezone(self, timezone_name):

        start_normalizer = TimezoneNormalizer(self.start_time, timezone_name)
        end_normalizer = TimezoneNormalizer(self.end_time, timezone_name)

        self.start_time = start_normalizer.get_maintcal_datetime().to_python_datetime()
        self.end_time = end_normalizer.get_maintcal_datetime().to_python_datetime()

        self._calculateDurationInQuanta()
        self._calculateDepth()


    def _calculateDurationInQuanta(self):
        """
        NOTE: we do NOT have to add a minute to the timedelta, because slots 
        are defined as follows:

        start = 0
        end   = 720

        NOT

        start = 0
        end   = 719

        """
        length_timedelta = self.end_time - self.start_time 
        length_in_minutes = timedelta_to_total_seconds(length_timedelta) / 60

        # How many "bits" does this time period cover?
        self.duration_in_quanta = int(length_in_minutes / float(granularity_in_minutes()))


    def _calculateDepth(self):
        """ 
            The depth represents the *maximum* number of services that
            can be performed at the same time. It is the total number of work units
            in this period divided by the hours in the period, rounded *up*.

            E.g.: if there are 8 work units scheduled in a 5 hour period, they can do
            at most 2 services at once.
        """

        work_quanta = self.work_units_in_quanta
        work_per_duration = float(work_quanta) / self.duration_in_quanta
        self.depth = int(math.ceil(work_per_duration))


    def bitstringForDepth(self, current_depth):
        """
            Generate the default bit string for a given depth.

            depth is one-based; current_depth is zero-based, so when they're equal 
            or current_depth is greater, we've met/exceeded the depth for that period
        """
        if self.depth > current_depth:
            return AVAIL_BIT * self.duration_in_quanta
        return UNAVAIL_BIT * self.duration_in_quanta


    def applyScheduledService(self, service):
        self.work_units_in_quanta -= service.quantaHandledByPeriod(self)

    
    def __str__(self):
        return repr(self.__dict__)


    def __repr__(self):
        return repr(self.__dict__)


