from maintcal.lib.times_available.schedule import Schedule 
from maintcal.lib.times_available.times_available_query import TimesAvailableQuery
from maintcal.lib.helpers import file_logger
from maintcal.model import db_sess, ScheduledMaintenance
from datetime import datetime
from pylons import config
import logging
import profile

class HTTP404Error(Exception):
    pass


class HTTP400Error(Exception):
    pass


class Calculator(object):
    """
        NOTE:

            The end datetime is the last valid start of an available time.

            The resulting available times do NOT have to all fit before the end_datetime,
            just their starting points.


        Assumptions:

            All default times, exception times, and currently scheduled service times are in UTC.

            Therefore the date and/or datetime information passed into this class will be
            assumed to be in UTC.

        NOTE about the end datetime:

            If a query is run as follows:

                start_datetime = MaintcalDatetime(2009, 11, 1, 0, 0, 0)
                end_datetime = MaintcalDatetime(2009, 11, 2, 0, 0, 0)

            It will give the same results as:

                start_datetime = MaintcalDatetime(2009, 11, 1, 0, 0, 0)
                end_datetime = MaintcalDatetime(2009, 11, 1, 23, 59, 00)

            Both of the above queries will include the final slot.
            However, this query:

                start_datetime = MaintcalDatetime(2009, 11, 1, 0, 0, 0)
                end_datetime = MaintcalDatetime(2009, 11, 1, 23, 58, 00)

            will exclude the final slot of the day.


        NOTE:

            start_maintcal_datetime has valid time information that is appropriate when converted
                to a local timezone.
            end_maintcal_datetime has valid time information that is appropriate when converted
                to a local timezone.
    """
    def calculate_times_available(self, maintenance_id, start_maintcal_datetime, end_maintcal_datetime, exclude_tentative=False):
        """
        This is the higher-level interface to the calculator that provides
        a more convenient interface to the controller.
        """
        start = datetime.now()

        maintenance = db_sess.query(ScheduledMaintenance).get(maintenance_id)
        if not maintenance:
            raise HTTP404Error("No such maintenance with id '%s'" % maintenance_id)

        calendar_ids = [service.calendar_id for service in maintenance.services]
        if not calendar_ids:
            raise HTTP400Error("Maintenance has no services associated with it.")

        if set(calendar_ids) & set(config['calculator_calendars']):
            #print calendar_ids
            #print config['calculator_calendars']
            #print set(calendar_ids) & set(config['calculator_calendars'])
            file_logger("[%s] maintenance_id: %s, cals:%s, start_dt:%s, end_dt:%s\n" % (datetime.now().isoformat(), maintenance_id, config['calculator_calendars'],start_maintcal_datetime, end_maintcal_datetime))
        query = TimesAvailableQuery(start_maintcal_datetime, end_maintcal_datetime, 
                maintenance.total_duration_in_quanta())

        # NOTE: times_available is a list of python datetimes
        times_available = self._perform_times_available_query(query, calendar_ids, exclude_tentative=exclude_tentative)

        end = datetime.now()

        # print "Times available calculation start: %s end: %s total: %s" % (start, end, end-start)

        if set(calendar_ids) & set(config['calculator_calendars']):
            #file_logger("  cals:%s, times_available:%s\n" % (config['calculator_calendars'],str(times_available)))
            file_logger("  cals:%s, times_available:\n" % config['calculator_calendars'])
            for single_time in times_available:
                file_logger("    %s\n" % single_time)
        return (times_available, maintenance.services, maintenance.total_duration())


    def verify_times_available(self,calendar_ids, start_maintcal_datetime, end_maintcal_datetime):
        """
            Performs a times available calculation for one or more calendars to ensure that any
            Schedules that have been entered are valid.Specifically trying to raise 
            InvalidDatetimeException and AmbiguousDatetimeException errors. 
            This uses a maintenance length of 1/2 hour to ensure that it can fit inside a 
            potentially invalid or ambiguous time block.
        """
        query = TimesAvailableQuery(start_maintcal_datetime, end_maintcal_datetime, 1)
        self._perform_times_available_query(query, calendar_ids)
        return True

    def _perform_times_available_query(self, query, calendar_ids, exclude_tentative=False):
        """
            Return a list of start_times for the time periods that can fit the specified service. 
        """

        schedules = self._getSchedules(calendar_ids, query, exclude_tentative=exclude_tentative)

        matches = []
        for schedule in schedules:
            #print "bitmask start:"
            #print datetime.now()
            matches.append(schedule.bitmask())
            #print "bitmask end:"
            #print datetime.now()

        if len(matches) == 0:
            return []

        s = set(matches[0])
        for m in matches:
            s = s.intersection(set(m))

        matches = list(s)
        matches.sort()

        #print "*****************************************************"
        #print "matches: %s" % matches

        return matches

    def _getSchedules(self, calendar_ids, query, exclude_tentative=False):
        schedules = []
        #print "schedule start:"
        #print datetime.now()
        for calendar_id in calendar_ids:
            schedule = Schedule(calendar_id, query, exclude_tentative=exclude_tentative)
            #print "schedule done:"
            #print datetime.now()
            schedules.append(schedule)

        return schedules

