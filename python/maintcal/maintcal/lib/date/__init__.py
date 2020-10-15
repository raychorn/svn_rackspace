"""
This package is to consolidate date and time manipulation inside of maintcal.

"""
from datetime import date
from datetime import datetime
from decimal import Decimal
import time

# This is a cache that maps timezone names to timezone abbreviations
# because the SQL to perform the lookup is relatively slow.
timezone_name_to_abbreviation = {}

class IncorrectDatetimeType(Exception):
    pass

# Misc date and time functionality


# Cache the symbol to avoid multiple imports, which is a known python performance bug
MaintcalDatetime = None

def get_database_utc_now():
    from maintcal.model import db_sess
    """
    Get current time in UTC from the database as a maintcal_datetime
    """
    global MaintcalDatetime
    if not MaintcalDatetime:
        from maintcal.lib.date.maintcal_datetime import MaintcalDatetime

    sql_query = "SELECT CURRENT_TIMESTAMP AT TIME ZONE 'UTC';"

    result = db_sess.execute(sql_query)
    result_python_datetime = result.fetchone()[0]
        
    maintcal_datetime = MaintcalDatetime.from_python_datetime(result_python_datetime)

    return maintcal_datetime

def datetime2timestamp(a_datetime):
    undsted_list = list(a_datetime.timetuple())
    undsted_list[-1] = -1
    undsted_tuple = tuple(undsted_list)
    return int(time.mktime(undsted_tuple))


def parse_str_date(v):
    """
    Not currently used, but might be soon.
    """
    time_tuple = time.strptime(v, "%m/%d/%Y %I:%M %p")
    time_tuple = tuple(list(time_tuple)[:-3])
    return datetime(*time_tuple)
    

def assertDatetime(a_wannabe_datetime):
    # We need to validate that this is a datetime and not a date since datetimes have
    # lots more information (and therefore operating on a date would be an undefined behavior.)
    if not hasattr(a_wannabe_datetime, "microsecond"):
        raise IncorrectDatetimeType("This variable needs to be a datetime.")


def seconds_to_hours(seconds):
    """Converts a number of seconds to the appropriate number of hours."""
    return seconds / float(3600) 


def date_to_datetime(a_date):
    """Converts a python datetime.date object into a datetime.datetime object."""
    # NOTE: we also make sure that microseconds are zero, because
    #       sometimes microseconds appears to be initialized to values like 3.
    return datetime(*a_date.timetuple()[:-2]).replace(microsecond=0)


def timedelta2hours(value):
    """Converts a timedelta object into hours. Ignores microseconds."""
    seconds_in_hours = Decimal(value.seconds) / Decimal(3600)
    return (value.days * 24) + float(seconds_in_hours)

def timedelta_to_total_seconds(timedelta):
    """Converts a timedelta to the total number of seconds.
       The main purpose of this function is to combine the days value
       with the seconds."""
    days_in_seconds = timedelta.days * 86400
    return days_in_seconds + timedelta.seconds

def js_dow(python_date):
    """python date weekday format is 0 = monday, 6 = sunday
       js date is 0 = sunday, 6 = saturday""" 
    # Handle the rollover of sunday from six back to zero
    if python_date.weekday() == 6:
        return 0
    else:
        return python_date.weekday() + 1 

def python_date_to_tuple(python_date):
    """ A simple tuple format for python dates. """
    return (python_date.year, python_date.month, python_date.day)
