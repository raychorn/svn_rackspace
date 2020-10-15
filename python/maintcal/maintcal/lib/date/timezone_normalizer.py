"""
There are two difficult situations to deal with.

zdump illustrates the two cases:

Case #1: The non-existent hour:

    ryan.springer@d-db1:~$ zdump -v US/Central | grep 2009 | grep Mar
    US/Central  Sun Mar  8 07:59:59 2009 UTC = Sun Mar  8 01:59:59 2009 CST isdst=0 gmtoff=-21600
    US/Central  Sun Mar  8 08:00:00 2009 UTC = Sun Mar  8 03:00:00 2009 CDT isdst=1 gmtoff=-18000

    If the client sends us 2:30 US/Central, this is not a validate datetime.

    I am going to raise a InvalidDatetimeException. 

Case #2: The ambiguous hour:

    ryan.springer@d-db1:~$ zdump -v US/Central | grep 2009 | grep Nov
    US/Central  Sun Nov  1 06:59:59 2009 UTC = Sun Nov  1 01:59:59 2009 CDT isdst=1 gmtoff=-18000
    US/Central  Sun Nov  1 07:00:00 2009 UTC = Sun Nov  1 01:00:00 2009 CST isdst=0 gmtoff=-21600

    If the client sends us 1:30 US/Central, this is an ambiguous datetime.

    I am going to raise an AmbiguousDatetimeException.

    If the user sends a daylight savings flag, 
    then we can automatically disambiguate the AmbiguousDatetimeException 
    and provide a correct UTC value.

================================================================================

Performance Issues:

    It is to slow to perform queries of the following type for each datetime:

        SELECT TIMESTAMP WITH TIME ZONE x AT TIME ZONE 'UTC';

    Instead, we will perform a query for the first conversion in such a way
    that it will return an "aware" python datetime.

    We will try to extract the tzinfo object from the aware python datetime and
    use it for all further computations involving the datetime.


TODO:

    -   Detect invalid datetimes and raise exceptions
    -   Detect ambiguous datetimes and raise exceptions

"""
from datetime import datetime
from maintcal.model import db_sess
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from maintcal.lib.date import timedelta_to_total_seconds
from datetime import timedelta
from sqlalchemy.exceptions import ProgrammingError
from maintcal.lib.date.timezone import TimezoneType, get_timezone_type

class InvalidDatetimeException(Exception):
    pass

class AmbiguousDatetimeException(Exception):
    pass


class TimezoneNormalizerTzFile(object):

    """
    Assumptions:

        This normalizer will fail if a timezone switches daylight savings time
        more than once within a 96 hour period.

    """

    def __init__(self, python_datetime, timezone_name, is_dst = None):
        """
        timezone_name is a full timezone name, not a timezone abbreviation

        The user can optionally pass a is_dst, which will only be
        used if the conversion will raise an AmbiguousDatetimeException.

        """
        # Raises ValueError() if timezone name is incorrect
        self.tzfile = get_timezone_type(timezone_name)

        self.timezone_name = timezone_name
        self._python_datetime = python_datetime
        self.is_dst = is_dst
        self._maintcal_datetime = None


    def get_maintcal_datetime(self):
        self._convert_python_datetime_to_utc()
        return self._maintcal_datetime

    def _convert_python_datetime_to_utc(self):
        if self._maintcal_datetime:
            return

        # First, we are going to try to find the correct timezone_type information
        (near_transition, timezone_type_start, timezone_type_end, transition_point_in_utc) = self._is_near_transition(
                self._python_datetime)

        #print self._python_datetime
        #print near_transition

        timezone_type = timezone_type_start

        if near_transition:
            # Get the transition point as a maintcal_datetime

            transition_datetime = MaintcalDatetime.from_timestamp(transition_point_in_utc)

            # If the offset of the older timezone is larger than the offset
            # of the newer timezone, then we will have to check for an ambiguous datetime

            if timezone_type_start.offset > timezone_type_end.offset:

                # Check for ambiguitiy

                # The start is bigger than the end, so get the difference

                delta_difference = timezone_type_start.offset - timezone_type_end.offset

                # Determine the window of ambiguity

                window_start_utc = transition_datetime.to_python_datetime()
                window_end_utc = window_start_utc + timedelta(seconds=delta_difference)

                # We will zone the window to the right in order to detect ambiguity
                # 
                # Determine the window of ambiguity in localized time 
                # Note: the datetimes are for the right side of the transition, but
                # we can use them to check if the datetime falls in the window anyway
                #
                # For nov 1 america/chicago 2009:
                #
                # In this example, I have actually calculated the UTC times as my window:
                #
                #  07:00:00 UTC   02:00:00 CDT    01:00:00 CST 
                #  08:00:00 UTC   03:00:00 CDT    02:00:00 CST 
                #
                # In order to check for ambiguity, I need to zone to CST, which would
                # be the "right" hand side of the transition, that is, the timezone_type_end

                window_start_local = window_start_utc + timezone_type_end.delta
                window_end_local = window_end_utc + timezone_type_end.delta
                if window_start_local <= self._python_datetime < window_end_local:
                    #print "==== Ambiguity!"

                    # Because zero is a valid choice, we directly compare against None
                    if self.is_dst is not None:
                        if self.is_dst == timezone_type_start.isdst:
                            # use the start
                            timezone_type = timezone_type_start
                        else:
                            # use the end
                            timezone_type = timezone_type_end
                    else:
                        raise AmbiguousDatetimeException('The datetime specified is ambiguous in the timezone specified due to DST time changes', self._python_datetime)

                elif self._python_datetime < window_start_local:
                    # Convert on the left
                    timezone_type = timezone_type_start

                else:
                    # Convert to the right
                    timezone_type = timezone_type_end
        
            else:

                # Check for nonexistence

                # The end is bigger than the start, so get the difference

                delta_difference = timezone_type_end.offset - timezone_type_start.offset

                # Determine the window of non-existence

                window_start_utc = transition_datetime.to_python_datetime()
                window_end_utc = window_start_utc + timedelta(seconds=delta_difference)

                # We will zone the window to the left in order to detect non-existence

                window_start_local = window_start_utc + timezone_type_start.delta
                window_end_local = window_end_utc + timezone_type_start.delta

                if window_start_local <= self._python_datetime < window_end_local:
                    #print "==== Nonexistence!"
                    raise InvalidDatetimeException("The datetime specified cannot exist in the timezone specified due to DST time changes", self._python_datetime)

                elif self._python_datetime < window_start_local:
                    # Convert on the left
                    timezone_type = timezone_type_start

                else:
                    # Convert to the right
                    timezone_type = timezone_type_end
 
        else:
            timezone_type = timezone_type_start

        localized_maintcal_datetime = MaintcalDatetime.from_python_datetime(self._python_datetime)

        # Convert the localized time into UTC
        self._maintcal_datetime = localized_maintcal_datetime.to_utc( timezone_type.delta )

    def _is_near_transition(self, python_datetime):
        """
        This will determine if the given python datetime is anywhere near
        a dst transition point.

        We are not sure if we are in dst or not, so we try and check
        
        We arbitrarily pretend our input value is utc, and then
        query everything from two days before to two days after to
        see if we get back the same timezone_type from both sides

        """

        python_datetime_query_start = python_datetime - timedelta(hours=48)
        maintcal_datetime_query_start = MaintcalDatetime.from_python_datetime(python_datetime_query_start)

        python_datetime_query_end = python_datetime + timedelta(hours=48)
        maintcal_datetime_query_end = MaintcalDatetime.from_python_datetime(python_datetime_query_end)

        timezone_type_of_start = self.tzfile.find_timezone_info_utc(maintcal_datetime_query_start)
        timezone_type_of_end = self.tzfile.find_timezone_info_utc(maintcal_datetime_query_end)

        # If timezone_type_of_start == timezone_type_of_end, 
        # we know that in 48 hours in either direction, pretending the
        # given time was UTC, we are in the same timezone_type, so we can just
        # use that timezone_type to do the conversion.

        near_transition = timezone_type_of_start != timezone_type_of_end

        transition_point_in_utc = None
        if near_transition:
            transition_point_in_utc = self.tzfile.find_previous_transition_point(maintcal_datetime_query_end)
        
        return (near_transition, timezone_type_of_start, timezone_type_of_end, transition_point_in_utc)




# Helpers
def change_python_datetime_timezone(source_datetime, from_zonename=None, to_zonename=None):
    # args are year, month, day, hours, minutes, seconds, from_tz_name, to_tz_name
    query_template = "SELECT TIMESTAMP WITH TIME ZONE '%s-%s-%s %s:%s:%s %s' AT TIME ZONE '%s';"
    # this gets us year, month, day, hours, minutes, seconds
    query_args = list(source_datetime.timetuple())[:6]
    query_args.extend([from_zonename, to_zonename])
    query = query_template % tuple(query_args)
    try:
        result = db_sess.execute(query)
    except ProgrammingError, e:
        raise ValueError("Incorrect datetime and/or timezone input.")
    return result.fetchone()[0]

class TimezoneNormalizer_postgres(object):
    """
    """

    def __init__(self, python_datetime, timezone_name, is_dst = None):
        """
        timezone_name is a full timezone name, not a timezone abbreviation

        The user can optionally pass a is_dst, which will only be
        used if the conversion will raise an AmbiguousDatetimeException.

        """
        self.timezone_name = timezone_name
        self._python_datetime = python_datetime
        self._maintcal_datetime = None

    def get_maintcal_datetime(self):
        # Why are we passing in arguments here? self.fn(self.arg) means get rid of arg
        self._convert_python_datetime_to_utc()
        return self._maintcal_datetime

    def _check_python_datetime_is_valid(self):
        utc_python_datetime = change_python_datetime_timezone(self._python_datetime, from_zonename=self.timezone_name, to_zonename='utc')
        zoned_python_datetime  = change_python_datetime_timezone(utc_python_datetime, from_zonename='utc', to_zonename=self.timezone_name)

        # If the datetime that we have roundtripped to UTC and back is not the same
        # as the original datetime, then we are dealing with a nonexistent datetime
        if zoned_python_datetime != self._python_datetime:
            raise InvalidDatetimeException("The datetime specified cannot exist in the timezone specified due to DST time changes", zone_python_datetime)

    def _check_python_datetime_is_distinct(self):
        # Check for an ambiguous timespan of 30, 60, 90, or 120 minutes since the world is not standardized on a DST hour
        for span_in_minutes in [30, 60, 90, 120]:
            zoned_earlier_python_datetime = self._calculate_earlier_datetime(self._python_datetime, span_in_minutes)
            zoned_later_python_datetime = self._calculate_later_datetime(self._python_datetime, span_in_minutes)

            if self._python_datetime == zoned_earlier_python_datetime \
            or self._python_datetime == zoned_later_python_datetime:
                raise AmbiguousDatetimeException('The datetime specified is ambiguous in the timezone specified due to DST time changes', self._python_datetime)

    def _calculate_earlier_datetime(self, zoned_python_datetime, span_in_minutes):
        utc_python_datetime = change_python_datetime_timezone(zoned_python_datetime, from_zonename=self.timezone_name, to_zonename='utc')
        utc_earlier_python_datetime = utc_python_datetime - timedelta(minutes=span_in_minutes)
        zoned_earlier_python_datetime = change_python_datetime_timezone(utc_earlier_python_datetime, from_zonename='utc', to_zonename=self.timezone_name)
        return zoned_earlier_python_datetime

    def _calculate_later_datetime(self, zoned_python_datetime, span_in_minutes):
        utc_python_datetime = change_python_datetime_timezone(zoned_python_datetime, from_zonename=self.timezone_name, to_zonename='utc')
        utc_later_python_datetime = utc_python_datetime + timedelta(minutes=span_in_minutes)
        zoned_later_python_datetime = change_python_datetime_timezone(utc_later_python_datetime, from_zonename='utc', to_zonename=self.timezone_name)
        return zoned_later_python_datetime
        
    def _convert_python_datetime_to_utc(self):
        if self._maintcal_datetime:
            return
        self._check_python_datetime_is_valid()
        self._check_python_datetime_is_distinct()
        utc_python_datetime = change_python_datetime_timezone(self._python_datetime, from_zonename=self.timezone_name, to_zonename='utc')
        self._maintcal_datetime = MaintcalDatetime.from_python_datetime(utc_python_datetime)

#TimezoneNormalizer = TimezoneNormalizer_postgres
TimezoneNormalizer = TimezoneNormalizerTzFile
