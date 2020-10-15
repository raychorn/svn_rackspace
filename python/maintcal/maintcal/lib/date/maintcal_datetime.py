import datetime
from maintcal.lib.date import seconds_to_hours
from maintcal.lib.date import date_to_datetime 
from maintcal.lib.date import timedelta_to_total_seconds

TimezoneRenderer = None
MaintcalDate = None
EPOCHORDINAL = datetime.datetime.utcfromtimestamp(0).toordinal()


class MaintcalDatetime(object):
    """
    The purpose of this class is to provide a consistent and clean way
    to interact with datetimes inside of the maintenance calendar application.

    NOTE: we don't care about microseconds.

    NOTE: we also don't care about timezones.  
          Every MaintcalDatetime is assumed to be in UTC

    All conversions to and from UTC will be handled externally from this class.
    """

    _list_days_before_month = [ 0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334 ]

    def __init__(self, year, month, day, hour, minute, second):
        """
        month is 0 to 11
        hour is 0 to 23
        minute is 0 to 59
        second is 0 to 59
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def __eq__(self, other):
        if other is None:
            return False

        return self.year == other.year and self.month == other.month and self.day == other.day \
                and self.hour == other.hour and self.minute ==other.minute and self.second == other.second

    def __str__(self):
        return "MaintcalDateTime is %4d-%02d-%02d %02d:%02d:%02d UTC" % (
                self.year, self.month, self.day, self.hour, self.minute, self.second)

    def __repr__(self):
        return "MaintcalDateTime(%4d,%02d,%02d,%02d,%02d,%02d)" % (
                self.year, self.month, self.day, self.hour, self.minute, self.second)

    def to_python_date(self):
       """ Return a datetime.date object. """
       return datetime.date(self.year, self.month, self.day)

    def to_timestamp(self):
        return ((self.to_ordinal() - EPOCHORDINAL) * 86400
                     + self.hour * 3600
                     + self.minute * 60
                     + self.second)

    @classmethod
    def from_timestamp(cls, timestamp):
        utc_datetime = datetime.datetime.utcfromtimestamp(timestamp)
        return MaintcalDatetime(utc_datetime.year, utc_datetime.month, utc_datetime.day,
                            utc_datetime.hour, utc_datetime.minute, utc_datetime.second)

    def to_localtime(self, delta):
        delta_in_secs = timedelta_to_total_seconds( delta ) 
        timestamp = self.to_timestamp()
        timestamp = delta_in_secs + timestamp
        return MaintcalDatetime.from_timestamp( timestamp )

    def to_utc(self, delta):
        delta_in_secs = timedelta_to_total_seconds( delta ) 
        timestamp = self.to_timestamp()
        timestamp = timestamp - delta_in_secs
        return MaintcalDatetime.from_timestamp( timestamp )

    @classmethod
    def _is_leap(cls, year):
        # trust me
        return (year % 4) == 0 and ((year % 100) != 0 or (year % 400) == 0)

    @classmethod
    def _days_before_month(cls, year, month):
        #assert month >= 1
        #assert month <= 12
        days = MaintcalDatetime._list_days_before_month[month]
        if month > 2 and MaintcalDatetime._is_leap(year):
            days = days + 1
        return days

    @classmethod
    def _days_before_year(cls, year):
        y = year - 1;
        # This is incorrect if year <= 0; we really want the floor
        # here.  But so long as MINYEAR is 1, the smallest year this
        # can see is 0 (this can happen in some normalization endcases),
        # so we'll just special-case that.
        assert year >= 0
        if y >= 0:
            return y * 365 + y/4 - y/100 + y/400
        else:
            assert y == -1
            return -366

    @classmethod
    def _ymd_to_ord(self, year, month, day):
        return MaintcalDatetime._days_before_year( year ) + \
                MaintcalDatetime._days_before_month( year, month ) + day 

    def to_ordinal(self):
        return MaintcalDatetime._ymd_to_ord( self.year, self.month, self.day )

    # python date / python datetime conversions

    @classmethod
    def from_python_date(cls, python_date):
        """ Return a MaintcalDate object. """
        return cls(python_date.year, python_date.month, python_date.day, 0, 0, 0)

    def to_python_datetime(self, timezone_name = None):
        if not timezone_name or timezone_name == 'UTC':
            # Plug microseconds at zero and timezone at UTC
            return datetime.datetime(self.year, self.month, self.day, self.hour, self.minute, self.second, 0)

        # Render to the chosen timezone name
        # We do some manual caching of the renderer import to avoid a performance hit
        # see the python performance FAQ for more info
        global TimezoneRenderer
        if not TimezoneRenderer:
            from maintcal.lib.date.timezone_renderer import TimezoneRenderer

        time_renderer = TimezoneRenderer(timezone_name)
        time_tuples = time_renderer.get_javascript_time_tuples([self])
        return datetime.datetime(*time_tuples[0][0:6])

    @classmethod
    def from_python_datetime(cls, python_datetime):
        return cls(python_datetime.year, python_datetime.month, python_datetime.day,
                python_datetime.hour, python_datetime.minute, python_datetime.second)

    def js_dow(self):
        """python date weekday format is 0 = monday, 6 = sunday
           js date is 0 = sunday, 6 = saturday"""
        python_day_of_week = self.to_python_datetime().weekday()
        # Handle the rollover of sunday from six back to zero
        if python_day_of_week == 6:
            return 0
        else:
            return python_day_of_week + 1

    def to_tuple(self):
        return (self.year, self.month, self.day, self.hour, self.minute, self.second)

    def to_dict(self):
        return {'year':self.year, 'month':self.month, 'day':self.day, 'hour':self.hour, 'minute':self.minute, 'second':self.second}

    # maintcal date conversions

    # to maintcal date ooh bad name!~
    def to_date(self):
        """ Return a MaintcalDate object. """
        global MaintcalDate
        if not MaintcalDate:
            from maintcal.lib.date.maintcal_date import MaintcalDate
        return MaintcalDate.from_datetime(self)

    @classmethod
    def from_date(cls, date):
        """ Build a new MaintcalDatetime from a MaintcalDate. """
        return MaintcalDatetime(date.year, date.month, date.day, 0, 0, 0)

    @classmethod
    def to_maintcal_zoned_datetime(cls, self, timezone_name):
       return MaintcalZonedDatetime.from_maintcal_datetime(self, timezone_name)



