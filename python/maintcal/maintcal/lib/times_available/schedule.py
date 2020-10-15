from datetime import datetime, date, timedelta
from maintcal.lib.times_available import bitstring_and, granularity_in_minutes
from maintcal.lib.times_available.period import Period 
from maintcal.lib.times_available import UNAVAIL_BIT
from maintcal.model import db_sess, AvailableDefaults, AvailableExceptions, ScheduledService, Calendar
from sqlalchemy import and_
from maintcal.lib.date.timezone_normalizer import TimezoneNormalizer
from maintcal.lib.date import seconds_to_hours
from maintcal.lib.date import timedelta_to_total_seconds
from maintcal.lib.helpers import file_logger
from pylons import config

class InvalidPeriodError(Exception):
    pass

class Schedule(object):
    """ 
        This class represents the scheduling information for a specific calendar
        for a specific date range.
    """

    def __init__(self, calendar_id, query, exclude_tentative=False):

        self.query = query

        #   Load the defaults

        self.available_defaults = db_sess.query(AvailableDefaults).filter(AvailableDefaults.calendar_id == calendar_id).all()

        #   Load the calendar, to get the timezone_name

        calendar = db_sess.query(Calendar).get(calendar_id)
        self.calendar_id = calendar_id
        self.timezone_name = calendar.timezone

        #print "timezone_name: %s" % self.timezone_name

        #   Grab a copy of the query's start and end datetimes in utc

        self.query_utc_start = query.start_maintcal_datetime.to_python_datetime()
        self.query_utc_end = query.end_maintcal_datetime.to_python_datetime()

        #print "query_utc_start: %s  query_utc_end: %s" % (self.query_utc_start, self.query_utc_end)

        #   Localize the query start and end times, and load the appropriate exceptions

        self.query_localized_start = query.start_maintcal_datetime.to_python_datetime(self.timezone_name)
        self.query_localized_end = query.end_maintcal_datetime.to_python_datetime(self.timezone_name)

        #print "query_localized_start: %s  query_localized_end: %s" % (self.query_localized_start, self.query_localized_end)

        self.exceptions = db_sess.query(AvailableExceptions).filter(
            and_(AvailableExceptions.exception_date >= self.query_localized_start.date(),
                 AvailableExceptions.exception_date <= self.query_localized_end.date(),
                 AvailableExceptions.calendar_id == calendar_id)).all()

        #
        #   Get the bounding box for the dates of the localized query
        #   The "Bounding box" datetimes are ONLY used in order to query scheduled_services
        #   The actual date range for the calculation will be based on the query_localized datetimes.
        #

        #   The bounding box is the date time range that contains the first minute of the date 
        #   of the localized_start up to the last minute of the last day of the bounding start

        self.bounding_box_localized_start = self.query_localized_start.replace(hour=0,minute=0,second=0)
        self.bounding_box_localized_end = self.query_localized_end.replace(hour=23,minute=59,second=59)

        #print "bounding_box_localized_start: %s  bounding_box_localized_end: %s" % (
        #        self.bounding_box_localized_start, self.bounding_box_localized_end)

        #   Normalize the bounding box datetimes into UTC for the scheduled_services query

        start_normalizer = TimezoneNormalizer(self.bounding_box_localized_start, self.timezone_name)
        end_normalizer = TimezoneNormalizer(self.bounding_box_localized_end, self.timezone_name)

        self.bounding_box_utc_start = start_normalizer.get_maintcal_datetime()
        self.bounding_box_utc_end = end_normalizer.get_maintcal_datetime()

        #print "bounding_box_utc_start: %s  bounding_box_utc_end: %s" % (
        #        self.bounding_box_utc_start, self.bounding_box_utc_end)

        # NOTE: Include past_due services because they are still scheduled and may just be a
        #       long-running service that the maintcal cron job has marked as past_due.
        #       So we do not want to allow people to schedule during a past_due service,
        #       which is probably the cause of the IAD overbooking problems.
        if exclude_tentative:
            status_list = [ScheduledService.State.SCHEDULED,ScheduledService.State.PAST_DUE]
        else:
            status_list = [ScheduledService.State.SCHEDULED,ScheduledService.State.PAST_DUE,ScheduledService.State.TENTATIVE]

        #ScheduledService.state_id.in_(status_tuple),
        self.scheduled_services = db_sess.query(ScheduledService).filter(
            and_(ScheduledService.start_time <= self.bounding_box_utc_end,
                ScheduledService.end_time >= self.bounding_box_utc_start,
                ScheduledService.state_id.in_(status_list),
                ScheduledService.calendar_id == calendar_id)).all()

        # A schedule contains 1 or more Periods
        self.periods = []

        self._start_time = None


    def bitmask(self):
        """ Gets the availablity mask for this schedule's calendar for this schedule's date range."""

        # Iterate over the dates and populate the periods

        current_date = self.bounding_box_localized_start.date()
        end_date = self.bounding_box_localized_end.date()

        while current_date <= end_date:
            self.populatePeriods(current_date)
            current_date += timedelta(days=1)
        #print "done populating periods: " + repr(datetime.now())

        if not self.periods:
            return ('', self._start_time)

        #
        #   Check for problems with the periods not being consecutive.
        #

        #   Sort the periods for the validation
        self.periods.sort(lambda x,y: cmp(x.start_time, y.start_time))

        check_date = None
        for p in self.periods:
            if check_date:
                if check_date != p.start_time:
                    raise InvalidPeriodError
            check_date = p.end_time

        # Normalize the periods to UTC

        if self.calendar_id in config['calculator_calendars']:
            file_logger("  iterating over localized periods:\n")
            for p in self.periods:
                file_logger("    period start time: %s  end time: %s\n" % (p.start_time, p.end_time))

        for p in self.periods:
            p.normalize_from_timezone(self.timezone_name)

        #print "done normalizing periods: " + repr(datetime.now())

        if self.calendar_id in config['calculator_calendars']:
            file_logger("  iterating over normalized periods:\n")
            for p in self.periods:
                file_logger("    period start time: %s  end time: %s\n" % (p.start_time, p.end_time))
        
        if self.calendar_id in config['calculator_calendars']:
            file_logger("  iterating over scheduled services:\n")
            for service in self.scheduled_services:
                service_start = service.start_time.to_python_datetime()
                service_end = service.end_time.to_python_datetime()
                file_logger("    service start time: %s  end time: %s\n" % (service_start, service_end))

        # NOTE: all of the periods should be contiguous because the end time
        # of each period should be the exact same datetime as the start of
        # the next period.
        # Therefore each period should be contiguous after the normalization

        # We now have all of the relevant periods in UTC

        self.applyScheduledItems()
        #print "done applying scheduled items: " + repr(datetime.now())

        # Perform the query

        self._matches = []
        self._performQuery()

        #print "done performing query: " + repr(datetime.now())
        
        #print self._matches
        return self._matches

    def _performQuery(self):
        """
        This is primarily to get around issues where a period of 1 hr has 1 quanta
        available and it still renders a bitmask of 11, which then happily
        matches a query of 1 hr.
        """
        service_length_in_quanta = self.query.service_length_in_quanta

        search_mask = "1" * service_length_in_quanta 

        for current_depth, mask_for_depth in enumerate(self.masks_for_depth):
            for starting_position in xrange(len(mask_for_depth)):
                ending_position = starting_position + service_length_in_quanta
                #print starting_position, ending_position
                #print mask_for_depth
                if mask_for_depth[starting_position:ending_position] == search_mask:
                    starting_datetime = self._start_time + timedelta(seconds=60*(starting_position * granularity_in_minutes()))
                    ending_datetime = self._start_time + timedelta(seconds=60*(ending_position * granularity_in_minutes()))

                    #print "match ", starting_datetime, ending_datetime
                    cleanly_applies = self._does_query_apply_cleanly(starting_datetime, ending_datetime)
                    #print "cleanly applies? %s" % cleanly_applies
                    if cleanly_applies:
                        self._matches.append(starting_datetime)

        good_bitmask = ""
        return good_bitmask


    def _does_query_apply_cleanly(self, start, end):

        #print "_does_query_apply_cleanly"
        #print "start: %s end: %s query_utc_start %s query_utc_end %s" % (repr(start), repr(end), repr(self.query_utc_start), repr(self.query_utc_end))

        # first ensure that the start and end range is valid for the query
        if not (self.query_utc_start <= start <= self.query_utc_end):
            #print "false 1"
            return False

        if end <= self.query_utc_start:
            #print "false 2"
            return False

        # This allows a minute of 59 to pass
        if end > (self.query_utc_end + timedelta(minutes=1)):
            #print "false 3"
            return False

        # Now check if the start and end applies cleanly to each period
        for period in self.periods:
            #print "period: %s" % repr(period)
            if period.start_time < end and period.end_time > start:
    
                #print "branch true"
                # Determine how many of the query's quantas need to fit inside of this period

                quanta_handled_by_period = self._quantaHandledByPeriod(start, end, period)

                if period.work_units_in_quanta < quanta_handled_by_period:
                    #print "false 4"
                    return False

        return True

    def _quantaHandledByPeriod(self, start_datetime, end_datetime, period):

        total_quanta = 0

        # Iterate through the quanta of the period, while the starting_quanta is less
        # than the ending quanta

        quanta_start_time = period.start_time
        while quanta_start_time < period.end_time:
            quanta_end_time = quanta_start_time + timedelta(minutes=granularity_in_minutes())

            if start_datetime <= quanta_start_time < end_datetime:
                if start_datetime < quanta_end_time <= end_datetime:
                    total_quanta = total_quanta + 1

            quanta_start_time = quanta_start_time + timedelta(minutes=granularity_in_minutes())

        return total_quanta


    def populatePeriods(self, current_date):
        """ 
        Use the defined times for this date if they exist; otherwise,
        use the default for that day of the week.

        Note: if a date has one or more blocked_time records, then we ignore
        the default times for that date.  That is, the available_exception records replace the entire day.
        """

        ret = [rec for rec in self.exceptions if rec.exception_date == current_date]
        if ret:
            ret.sort(lambda x,y: cmp(x.start_minutes, y.start_minutes))
            for rec in ret:
                period = Period(current_date=current_date, start_min=rec.start_minutes, end_min=rec.end_minutes,
                            work_units_in_quanta=rec.work_units_in_quanta)
                self.periods.append(period)
            return

        # Nothing special set for that date, so use the default for the DOW.

        ret = [rec for rec in self.available_defaults if rec.dow == current_date.weekday()]

        ret.sort(lambda x,y: cmp(x.start_minutes, y.start_minutes))
        for rec in ret:
            period = Period(current_date=current_date, start_min=rec.start_minutes, end_min=rec.end_minutes,
                            work_units_in_quanta=rec.work_units_in_quanta)
            self.periods.append(period)


    def applyScheduledItems(self):
        self._calculateMaxPeriodDepth()
        self._calculateMasksForDepths()

        #print "THIS IS THE ANSWER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        #print "before application"
        #for current_depth in xrange(self._max_period_depth):
        #    print self.masks_for_depth[current_depth]

        for svc in self.scheduled_services:
            #print "scheduled service: "
            self._applyScheduledService(svc)

            #print "After application"
            #for current_depth in xrange(self._max_period_depth):
            #    print self.masks_for_depth[current_depth]

            self._normalizeBitmasks()

            #print "After normalization"
            #for current_depth in xrange(self._max_period_depth):
            #    print self.masks_for_depth[current_depth]

        #print "After all applications"
        #for current_depth in xrange(self._max_period_depth):
        #    print self.masks_for_depth[current_depth]


    def _normalizeBitmasks(self):
        """
        After applying a service, we can go from:

        11111111
        00111100

        to

        11110001
        00111100

        and thus, we would NOT match at depth one for a 6 quanta service,
        even though it would be valid, because the depth is two and there
        are 1s available in the second depth.

        Therefore, this algorithm will push all ones down to the lowest level,
        thus giving:

        11111101
        00110000
        """

        for current_depth, mask_for_depth in enumerate(self.masks_for_depth):
            # We cannot normalize the deepest level of depth
            if current_depth == self._max_period_depth:
                break

            #print "  normalizing depth %s" % current_depth
            #print "    bitmask: %s" % mask_for_depth

            # Iterate over the mask
    
            for position, bit_value in enumerate(mask_for_depth):

                # If the position is 1, move on to the next bit

                if bit_value == '1':
                    continue 

                #print "    Found zero bit at position %s" % position

                # The current position is a zero, try to swap it with a 1
                # from a deeper depth

                # The current_depth is zero-based but max_period_depth is one based!!!
                # if there are two levels of depth, max period depth will be 2

                for search_depth in xrange(current_depth, self._max_period_depth):
                    #print "    search_depth %s" % search_depth
                    if self.masks_for_depth[search_depth][position] == '1':
                        # painful way of doing single char replacement

                        #print "    Found replacement bit at depth: %s" % search_depth

                        tmp = list(self.masks_for_depth[search_depth])
                        tmp[position] = '0'
                        self.masks_for_depth[search_depth] = ''.join(tmp)

                        tmp2 = list(self.masks_for_depth[current_depth])
                        tmp2[position] = '1'
                        self.masks_for_depth[current_depth] = ''.join(tmp2)
                        mask_for_depth = self.masks_for_depth[current_depth]
                        break


    def _calculateMaxPeriodDepth(self):
        self._max_period_depth = 0
        for period in self.periods:
            self._max_period_depth = max(self._max_period_depth, period.depth)

    def _calculateMasksForDepths(self):
        """
        Build the bitmask for each depth
        """
        self.masks_for_depth = []
        for current_depth in xrange(self._max_period_depth):
            bitstring_for_depth = ""
            for period in self.periods:
                # build master mask list used below to build daily bit string
                bitstring_for_depth += period.bitstringForDepth(current_depth)
            #print 'bitstring_for_depth: %s' % bitstring_for_depth
            self.masks_for_depth.append(bitstring_for_depth)

        # Bitstring length
        # Catch issue where no available time is present ever.
        if not self.masks_for_depth:
            self._bitstring_length = 0
        else:
            self._bitstring_length = len(self.masks_for_depth[0])
        #print 'self._bitstring_length: %s' % self._bitstring_length
        self._start_time = self.periods[0].start_time
        #print 'self._start_time: %s' % self._start_time
        self._end_time = self.periods[len(self.periods)-1].end_time
        #print 'self._end_time: %s' % self._end_time


    def _get_service_mask(self, service):
        """
        NOTE: The service mask will have 0s where the service occurs and 1s
                otherwise.

              This is because it will be AND'd with the bitmask for depth
        """
        # service.start_time and service.end_time are utc python datetimes

        service_start = service.start_time.to_python_datetime()
        service_end = service.end_time.to_python_datetime()

        length_of_service_in_quanta = 0
        mask = ""
        current_time = self._start_time
        while current_time <= self._end_time:
            # NOTE: the comparision with the end cannot be <=
            # because the end of a service is on a half-hour boundary

            if service_start <= current_time < service_end: 
                mask += "0"
                length_of_service_in_quanta = length_of_service_in_quanta + 1 
            else:
                mask += "1"
            current_time = current_time + timedelta(minutes=30)

        mask = mask[:self._bitstring_length]
        return (length_of_service_in_quanta, mask)

    def _applyScheduledService(self, service):
        """Apply one scheduled service."""

        (length_of_service_in_quanta, svc_mask) = self._get_service_mask(service)

        # We need to try to find an item in masks 
        # that will be completely "flipped" by ANDing it with the mask.

        most_available_depth = None
        most_available_bits  = 0

        # Try to apply the service at each level of depth
        # from shallowest to deepest depth layer
        for current_depth, mask_for_depth in enumerate(self.masks_for_depth):

            temp_mask = bitstring_and(mask_for_depth, svc_mask)

            # unavailable time including this service
            unavailable_quanta_including_service = temp_mask.count(UNAVAIL_BIT)

            # unavailable time excluding this service
            unavailable_quanta_excluding_service = mask_for_depth.count(UNAVAIL_BIT)

            bits_changed = unavailable_quanta_including_service - unavailable_quanta_excluding_service

            # if the service was applied cleanly
            if bits_changed == length_of_service_in_quanta:
                #print "clean app"
                #print "temp_mask"
                #print temp_mask
                self.masks_for_depth[current_depth] = temp_mask
                #print "temp_mask"
                #print self.masks_for_depth[current_depth] 
                self.masks_for_depth[current_depth] = temp_mask
                self._applyScheduledServiceToPeriods(service)
                #print "temp_mask"
                #print self.masks_for_depth[current_depth] 
                return

            # keep track of the best possible application of the service
            if bits_changed > most_available_bits:
                most_available_depth = current_depth
                most_available_bits = bits_changed

    
        # If we could not apply the scheduled service, then see if we can overbook it
        # NOTE: Do not use "if most_available_depth" without the "is not None" 
        #       because a depth of zero will fail the conditional and not apply

        if most_available_depth is not None:
            self.overbookServiceAtDepth(svc_mask, most_available_depth)
            self._applyScheduledServiceToPeriods(service)

    def overbookServiceAtDepth(self, svc_mask, depth):
        """NOTE: this is overbooking."""
        self.masks_for_depth[depth] = bitstring_and(self.masks_for_depth[depth], svc_mask)

    def _applyScheduledServiceToPeriods(self, service):

        for pd in service.periodsOverlappingService(self.periods):

            if pd.isFull():
                continue

            pd.applyScheduledService(service)

            if pd.isFull():
                self._removeAvailableTimeOfPeriodFromMasks(pd)

    def _removeAvailableTimeOfPeriodFromMasks(self, period):
        """ Remove all available time in the period from the masks """

        # Generate a mask of the correct width, with the period blanked out

        blank_period_mask = ""

        period_start = period.start_time
        period_end = period.end_time

        seconds_per_quanta = 60 * granularity_in_minutes()

        number_of_left_ones = timedelta_to_total_seconds(period_start - self._start_time) / seconds_per_quanta
        number_of_right_ones = timedelta_to_total_seconds(self._end_time - period_end) / seconds_per_quanta
        number_of_zeros = timedelta_to_total_seconds(period_end - period_start) / seconds_per_quanta

        left = number_of_left_ones * "1"
        center = number_of_zeros * "0"
        right = number_of_right_ones * "1"

        blank_period_mask = left + center + right

        #print 'blank_period_mask'
        #print blank_period_mask
        blank_period_mask = blank_period_mask[:self._bitstring_length]
 
        # Apply this mask to every level of depth

        for current_depth, mask in enumerate(self.masks_for_depth):
            self.masks_for_depth[current_depth] = bitstring_and(mask, blank_period_mask)
