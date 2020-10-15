"""
    We receive UTC MaintcalDatetime objects from the db or application logic.
    We output a tuple of information from the converted datetimes to the browser.

Performance Goal:

- Be able to handle 1000 to 10000 conversions in under a second

"""
from maintcal.model import db_sess
from maintcal.lib.date import timedelta_to_total_seconds
from maintcal.lib.date import timezone_name_to_abbreviation
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from sqlalchemy.exceptions import ProgrammingError

from maintcal.lib.date.timezone import TimezoneType, get_timezone_type
from datetime import datetime
import datetime

class TimezoneRendererTzFile(object):
    
    def __init__(self, timezone_name):
        # Raises ValueError() if timezone name is incorrect
        self.tzfile = get_timezone_type(timezone_name)
        self.timezone_name = timezone_name

    def as_timezone(self, utc_maintcal_datetime):
        """
        Converts from a UTC datetime to a localized datetime
        """
        # Get the localized time info from the olsen database
        ttinfo = self.tzfile.find_timezone_info_utc(utc_maintcal_datetime)

        # Get the offset, dst flag and tz abbreviation
        offset_in_seconds = timedelta_to_total_seconds( ttinfo.delta )
        is_dst = ttinfo.isdst
        tz_abbr = ttinfo.abbr

        localized_maintcal_datetime = utc_maintcal_datetime.to_localtime( ttinfo.delta )

        return (localized_maintcal_datetime, offset_in_seconds, is_dst, tz_abbr )

    def get_javascript_time_tuples(self, maintcal_datetime_list ):
        return map( self._get_javascript_time_tuple, maintcal_datetime_list )


    def _get_javascript_time_tuple(self, maintcal_datetime):

        if maintcal_datetime == None:
            return (0, 0, 0, 0, 0, 0, 0, u'UTC', 'UTC')

        (localized_maintcal_datetime, offset_in_seconds, is_dst, tz_abbr) = \
            self.as_timezone( maintcal_datetime )

        time_list = []
        time_list.append(localized_maintcal_datetime.year)
        time_list.append(localized_maintcal_datetime.month)
        time_list.append(localized_maintcal_datetime.day)
        time_list.append(localized_maintcal_datetime.hour)
        time_list.append(localized_maintcal_datetime.minute)
        time_list.append(localized_maintcal_datetime.second)
        time_list.append(offset_in_seconds)
        time_list.append(self.timezone_name)
        time_list.append(tz_abbr)
        time_list.append(is_dst)

        return tuple(time_list)


class TimezoneRendererPro(object):
    """
    """
    def __init__(self, timezone_name):
        """
        timezone_name is a full timezone name, not a timezone abbreviation
        """
        self.timezone_name = timezone_name
        self._lookup_timezone_abbreviation()

    def get_javascript_time_tuples(self, maintcal_datetime_list ):

        sql_query = self._build_sql_query(maintcal_datetime_list)
        try:
            result = db_sess.execute(sql_query)
        except ProgrammingError, e:
            raise ValueError("Incorrect datetime and/or timezone input.")

        # Run _get_javascript_time_tuple for each of the timezone conversions 
        # we got back from the server.
        return map( self._get_javascript_time_tuple, result.fetchone(), maintcal_datetime_list )

    def _get_javascript_time_tuple(self, timezoned_python_datetime, utc_maintcal_datetime):
        # NOTE: The utc_offset in pg_timezone_names is calculated for a given timezone 
        # based on the CURRENT_TIMESTAMP of the postgresql server, so any daylight savings
        # changes based on the actual maintcal_datetime being in a different daylight savings
        # situation would not be visible.
        # Therefore we cannot directly query utc_offset from pg_timezone_names.

        # NOTE: ORDER IS SIGNIFICANT IN THE FOLLOWING SUBTRACTION:
        #       The (possibly) non-UTC datetime should come before the guaranteed UTC datetime
    
        # Scheduled services could send us a None in the list
        if utc_maintcal_datetime == None:
            return (0, 0, 0, 0, 0, 0, 0, u'UTC', 'UTC')

        utc_timedelta = timezoned_python_datetime - utc_maintcal_datetime.to_python_datetime()
        utc_offset_in_seconds = timedelta_to_total_seconds(utc_timedelta)

        time_list = []
        time_list.append(timezoned_python_datetime.date().year)
        time_list.append(timezoned_python_datetime.date().month)
        time_list.append(timezoned_python_datetime.date().day)
        time_list.append(timezoned_python_datetime.time().hour)
        time_list.append(timezoned_python_datetime.time().minute)
        time_list.append(timezoned_python_datetime.time().second)
        time_list.append(utc_offset_in_seconds)
        time_list.append(self.timezone_name)
        time_list.append(self.timezone_abbreviation)
        return tuple(time_list)

    def _build_sql_query(self, maintcal_datetime_list):
        sql_columns = []
        for maintcal_datetime in maintcal_datetime_list:
            # ScheduledService might give us a None, we handle that here
            if maintcal_datetime == None:
                maintcal_datetime = MaintcalDatetime( 1,1,1,0,0,0 )

            sql_column = "TIMESTAMP WITH TIME ZONE '%(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s UTC' "\
                    "AT TIME ZONE '%(timezone_name)s'" % self._merge_dict( maintcal_datetime.to_dict(), { 'timezone_name': self.timezone_name } )
            sql_columns.append(sql_column)

        return "SELECT " + ",".join(sql_columns)

    def _merge_dict(self, dict1, dict2):
        return dict( dict1.items() + dict2.items() )

    def _lookup_timezone_abbreviation(self):
        """
        Note:   We make sure that we cache the timezone name to abbreviation lookups
                because the SQL query is relatively slow.
        """
        if self.timezone_name not in timezone_name_to_abbreviation:

            try:
                sql_query = "SELECT abbrev FROM pg_timezone_names WHERE name='%s';" % self.timezone_name
                result_proxy = db_sess.execute(sql_query)
            except ProgrammingError, e:
                raise ValueError("Incorrect timezone input.")

            try:
                result = result_proxy.fetchone()
                timezone_name_to_abbreviation[self.timezone_name] = result[0]
            except TypeError, e:
                raise ValueError("Incorrect timezone input.")

        self.timezone_abbreviation = timezone_name_to_abbreviation[self.timezone_name]


class TimezoneRenderer(object):
    """
    """
    def __init__(self, maintcal_datetime, timezone_name):
        """
        timezone_name is a full timezone name, not a timezone abbreviation
        """
        self.timezone_name = timezone_name
        self._lookup_timezone_abbreviation()

        if maintcal_datetime is None:
            self.year = 0
            self.month = 0
            self.day = 0
            self.hour = 0
            self.minute = 0
            self.second = 0
            self.utc_offset_in_seconds = 0
        else:
            self._convert_to_specified_timezone(maintcal_datetime)

    def get_javascript_time_tuple(self):
        time_list = []
        time_list.append(self.year)
        time_list.append(self.month)
        time_list.append(self.day)
        time_list.append(self.hour)
        time_list.append(self.minute)
        time_list.append(self.second)
        time_list.append(self.utc_offset_in_seconds)
        time_list.append(self.timezone_name)
        time_list.append(self.timezone_abbreviation)

        return tuple(time_list)

    def _convert_to_specified_timezone(self, maintcal_datetime):

        year = maintcal_datetime.year
        month = maintcal_datetime.month
        day = maintcal_datetime.day
        hour = maintcal_datetime.hour
        minute = maintcal_datetime.minute
        second = maintcal_datetime.second
        timezone_name = self.timezone_name

        try:
            sql_query = "SELECT TIMESTAMP WITH TIME ZONE '%(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s UTC' " \
                        "AT TIME ZONE '%(timezone_name)s';" % locals()
            result = db_sess.execute(sql_query)
        except ProgrammingError, e:
            raise ValueError("Incorrect datetime and/or timezone input.")

        result_python_datetime = result.fetchone()[0]

        self.year = result_python_datetime.year
        self.month = result_python_datetime.month
        self.day = result_python_datetime.day
        self.hour = result_python_datetime.hour
        self.minute = result_python_datetime.minute
        self.second = result_python_datetime.second

        # NOTE: The utc_offset in pg_timezone_names is calculated for a given timezone 
        # based on the CURRENT_TIMESTAMP of the postgresql server, so any daylight savings
        # changes based on the actual maintcal_datetime being in a different daylight savings
        # situation would not be visible.
        # Therefore we cannot directly query utc_offset from pg_timezone_names.

        # NOTE: ORDER IS SIGNIFICANT IN THE FOLLOWING SUBTRACTION:
        #       The (possibly) non-UTC datetime should come before the guaranteed UTC datetime
        utc_timedelta = result_python_datetime - maintcal_datetime.to_python_datetime()
        self.utc_offset_in_seconds = timedelta_to_total_seconds(utc_timedelta)

    def _lookup_timezone_abbreviation(self):
        """
        Note:   We make sure that we cache the timezone name to abbreviation lookups
                because the SQL query is relatively slow.
        """
        if self.timezone_name not in timezone_name_to_abbreviation:

            try:
                sql_query = "SELECT abbrev FROM pg_timezone_names WHERE name='%s';" % self.timezone_name
                result_proxy = db_sess.execute(sql_query)
            except ProgrammingError, e:
                raise ValueError("Incorrect timezone input.")

            try:
                result = result_proxy.fetchone()
                timezone_name_to_abbreviation[self.timezone_name] = result[0]
            except TypeError, e:
                raise ValueError("Incorrect timezone input.")

        self.timezone_abbreviation = timezone_name_to_abbreviation[self.timezone_name]


# Which implementation to use?
TimezoneRenderer = TimezoneRendererTzFile
#TimezoneRenderer = TimezoneRendererPro


