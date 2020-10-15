from maintcal.lib.date import timedelta_to_total_seconds

MaintcalDatetime = None
TimezoneRenderer = None

class MaintcalDatetimeRange(object):
    """
    This class stores a start maintcal_datetime and an end maintcal_datetime.

    The purpose of this class is to express algorithms involving datetime ranges 
    in a cleaner, higher-level way.

    Datetimeranges are inclusive of their endpoints.
    """
    def __init__(self, start_maintcal_datetime, end_maintcal_datetime):
        self.start_datetime = start_maintcal_datetime
        self.end_datetime = end_maintcal_datetime

    @classmethod
    def from_python_datetimes(cls, start_python_datetime, end_python_datetime):
        # Import caching for performance - see python performance FAQ
        global MaintcalDatetime
        if not MaintcalDatetime:
            from maintcal.lib.date.maintcal_datetime import MaintcalDatetime

        start_maintcal_datetime = MaintcalDatetime.from_python_datetime(start_python_datetime)
        end_maintcal_datetime = MaintcalDatetime.from_python_datetime(end_python_datetime)

        return cls(start_maintcal_datetime, end_maintcal_datetime)

    def duration_in_minutes(self):
        """Return the different in minutes between end_datetime and start_datetime as a float."""
        python_start_datetime = self.start_datetime.to_python_datetime()
        python_end_datetime = self.end_datetime.to_python_datetime()

        difference = python_end_datetime - python_start_datetime

        seconds = timedelta_to_total_seconds(difference)
        minutes = float(seconds) / 60

        return minutes


    def get_javascript_time_tuples(self, timezone_name):
        """
        Return a date range array of the javascript time tuples 
        of the start and end datetimes.
        """
        # Import caching for performance - see python performance FAQ
        global TimezoneRenderer
        if not TimezoneRenderer:
            from maintcal.lib.date.timezone_renderer import TimezoneRenderer

        timezone_renderer = TimezoneRenderer( timezone_name )
        result = timezone_renderer.get_javascript_time_tuples( [ self.start_datetime, self.end_datetime ] )

        return [result[0], result[1]]

    def __eq__(self, other):
        return self.start_datetime == other.start_datetime and self.end_datetime == other.end_datetime
