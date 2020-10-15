from datetime import timedelta
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime

class MaintcalDateRange(object):
    """
    This class stores a start maintcal_date and an end maintcal_date.

    The purpose of this class is to express algorithms involving date ranges 
    in a cleaner, higher-level way.

    Dateranges are inclusive of their endpoints.

    """

    @classmethod
    def from_python_datetimes(cls, python_start_datetime, python_end_datetime):
        start_datetime = MaintcalDatetime.from_python_datetime(python_start_datetime)
        end_datetime = MaintcalDatetime.from_python_datetime(python_end_datetime)
        return cls(start_datetime, end_datetime)

    def __init__(self, start_maintcal_date, end_maintcal_date):
        self.start_date = start_maintcal_date
        self.end_date = end_maintcal_date


    def dates(self):
        """Returns an iterator that iterates between start_date and end_date."""
        current_date = self.start_date.to_python_date()
        python_end_date = self.end_date.to_python_date()

        while current_date <= python_end_date:
            yield current_date
            current_date += timedelta(days=1)

    def __eq__(self, other):
        return self.start_date == other.start_date and self.end_date == other.end_date

