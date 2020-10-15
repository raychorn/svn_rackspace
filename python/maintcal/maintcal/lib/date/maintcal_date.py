import datetime
from maintcal.lib.date import seconds_to_hours
from maintcal.lib.date import date_to_datetime
from maintcal.lib.date import timedelta_to_total_seconds

MaintcalDatetime = None

class MaintcalDate(object):
    """
    The purpose of this class is to provide a consistent and clean way
    to interact with dates inside of the maintenance calendar application.
    """
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def __eq__(self, other):
        return self.year == other.year and self.month == other.month and self.day == other.day

    # python date / python datetime conversions

    def to_python_date(self):
        """ Return a datetime.date object. """
        return datetime.date(self.year, self.month, self.day)

    @classmethod
    def from_python_date(cls, python_date):
        """ Return a MaintcalDate object. """
        return cls(python_date.year, python_date.month, python_date.day)

    def to_python_datetime(self):
        return date_to_datetime(self.to_python_date())

    @classmethod
    def from_python_datetime(cls, python_datetime):
        return cls(python_datetime.year, python_datetime.month, python_datetime.day)

    # maintcal datetime conversions

    def to_datetime(self):
        """ Return a MaintcalDatetime object. """
        global MaintcalDatetime
        if not MaintcalDatetime:
            from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
        return MaintcalDatetime.from_date(self)

    @classmethod
    def from_datetime(cls, maintcal_datetime):
        return cls(maintcal_datetime.year, maintcal_datetime.month, maintcal_datetime.day)
