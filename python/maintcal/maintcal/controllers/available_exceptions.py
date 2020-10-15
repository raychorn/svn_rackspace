"""
Conceptually, the user of this controller will not be performing CRUD operations on an individual
available_exceptions records.  Instead the user will be updating all of the available_exceptions for
a specific calendar and a specific date ( the ENTIRE day ).

Therefore, there will be only two exposed operations:

index    Display all of the available_times records for a given calendar and by a specified date range.
         This will include any exceptions within the query range and if they don't exist the available defaults
         will be used.
update   Set all of the available_times records for a given calendar and a given a specific date (an ENTIRE day).

Weekday numbers:

    python date weekday:
        0 = monday
        6 = sunday

    Database standard for available defaults:
            SAME AS python date weekday:

        0 = monday
        6 = sunday

"""
import logging
import simplejson
import urllib
import time
from datetime import datetime, timedelta, date

from maintcal.lib.base import *
from maintcal.lib.date import js_dow, python_date_to_tuple, get_database_utc_now, date_to_datetime
from maintcal.lib.date.timezone_normalizer import TimezoneNormalizer
from maintcal.lib.date.timezone_normalizer import InvalidDatetimeException, AmbiguousDatetimeException
from maintcal.lib import core_xmlrpc
from maintcal.model import db_sess, AvailableExceptions, AvailableDefaults, Calendar
from maintcal.lib.py2extjson import py2extjson
from sqlalchemy.exceptions import ProgrammingError
from maintcal.lib.times_available import granularity_in_minutes
from maintcal.lib.times_available.calculator import Calculator

from authkit.authorize.pylons_adaptors import authorize
from core_authkit.permissions import LoggedIn 
log = logging.getLogger(__name__)

def _get_python_date_from_string(date_string):
    try:
        date_strings = date_string.split(',')
        year = int(date_strings[0])
        month = int(date_strings[1])
        day = int(date_strings[2])
        python_date = datetime(year,month,day)
    except ValueError:
        abort(400,"Invalid input for dates in scheduled exceptions structure.")
    return python_date


class AvailableExceptionsController(BaseController):

    @authorize(LoggedIn())
    def index(self, calendar_id, query_start_time=None, query_end_time=None):
        """
        GET /available_exceptions/1
        Returns all available_defaults for a given calendar id.

        We will always require the start year, start month and a start_day.
        We will always require an end year, end month, end day.

        Timezone name is required.

        """

        # load the calendar so we can verify a valid calendar and a valid calendar timezone
        the_calendar = db_sess.query(Calendar).get(calendar_id)

        if not the_calendar:
            abort(400,"Calendar with id: %s not found" % calendar_id)

        # automatically assume the data being sent is for the zone of the calendar being modified.
        query_tz = the_calendar.timezone

        if not query_start_time:
            try:
                (query_start_time, query_end_time) = self._getStartAndEndMaintcalDatetimes(query_tz)
            except ValueError:
                abort(400,"Invalid dates for start or end times")

        # localized now

        utc_now = get_database_utc_now()

        localized_now = utc_now.to_python_datetime(query_tz).date() 

        defaults = db_sess.query(AvailableDefaults).filter_by(calendar_id=the_calendar.id).order_by(AvailableDefaults.start_minutes).all()
        exceptions_query = db_sess.query(AvailableExceptions).filter_by(calendar_id=the_calendar.id)
        exceptions_query = exceptions_query.filter("exception_date >= '%s'" % query_start_time.date())
        exceptions_query = exceptions_query.filter("exception_date <= '%s'" % query_end_time.date())
        exceptions_query = exceptions_query.order_by(AvailableExceptions.exception_date)
        exceptions_query = exceptions_query.order_by(AvailableExceptions.start_minutes)
        exceptions = exceptions_query.all()

        results = {}

        defaults_dict = AvailableDefaults.get_available_defaults_for_calendar(the_calendar.id,js_dow = False)

        query_date = query_start_time.date()
        while query_date <= query_end_time.date():
            # disable dates before today
            disabled = False
            if localized_now > query_date:
                disabled = True
                
            query_date_string = "%s,%s,%s" % python_date_to_tuple(query_date)
            # filter all the exceptions for this date into a list
            exceptions_for_date = [exception for exception in exceptions if exception.exception_date == query_date]
            if exceptions_for_date:
                for exception in exceptions_for_date:
                    if query_date_string not in results:
                        results[query_date_string] = []
                    exception_js_dict = exception.toJsDict()
                    exception_js_dict['disabled'] = disabled
                    results[query_date_string].append(exception_js_dict)

            # no exceptions for this date were found use a default.
            else:
                python_weekday = query_date.weekday()
                defaults_js_list = []
                for d in defaults_dict[python_weekday]:
                    d['disabled'] = disabled
                    defaults_js_list.append(d)
                results[query_date_string] = defaults_js_list
                
            query_date = query_date + timedelta(hours=24)

        return py2extjson.dumps(results)


    @authorize(LoggedIn())
    def update(self, calendar_id):
        """
        Set all of the exceptions for a given calendar_id.
        """

        cal = db_sess.query(Calendar).get(calendar_id)

        if not cal:
            abort(400,"Calendar with id: %s not found" % calendar_id)

        if config['use_auth'] and 'Admin' not in core_xmlrpc.Ticket.getRoles(cal.tckt_queue_id):
            abort(403, "User must be admin of associated queue to edit this calendar.")

        try:
            calendar_data_json = request.params.get('calendar_data')
            calendar_data = simplejson.loads(calendar_data_json)
        except:
            abort(500,"Invalid data structure.")

        last_modified = calendar_data['last_modified']
        del calendar_data['last_modified']

        try:
            keys = calendar_data.keys()
            vs = []
            for k in keys:
                vs.append(_get_python_date_from_string(k))

            vs.sort()

            python_start_date = vs[0]
            python_end_date = vs[6]

        except IndexError:
            abort(500,"Invalid data structure")

        # Delete old records

        exceptions_query = db_sess.query(AvailableExceptions).filter_by(calendar_id=calendar_id)
        exceptions_query = exceptions_query.filter("exception_date >= '%s'" % python_start_date)
        exceptions_query = exceptions_query.filter("exception_date <= '%s'" % python_end_date)
        old_exceptions = exceptions_query.all()

        # check to see if exceptions exist and if so check to see if the values we are getting back are
        # the most current. Due to inconsistencies on what is being passed back from the client. This code is being
        # removed. - Nathen Hinson 12/02/2009
        # if old_exceptions:
        #    current_modification_time = int(time.mktime(old_exceptions[0].modification_date.timetuple()))
            # this makes the assumption that all exceptions for a date are commited on the same transaction, therefore
            # will have identical modification dates.
        #    if last_modified and last_modified < current_modification_time: 
        #        error_text = "Schedule Exceptions have changed since you last viewed them. " +\
        #                 "Your changes have been discarded. Please reload the application."
        #        abort(500,error_text)

        db_sess.begin_nested()
        for exception in old_exceptions:
            db_sess.delete(exception)
        db_sess.commit()

        # grab all defaults

        defaults = db_sess.query(AvailableDefaults).filter_by(calendar_id=calendar_id).order_by(AvailableDefaults.start_minutes).all()

        # construct a dictionary keyed by 'dow'
        defaults_dict = {}
        for default in defaults:
            if default.dow not in defaults_dict:
                defaults_dict[default.dow] = []
            defaults_dict[default.dow].append(default)

        # iterate over the data from calendar_data

        db_sess.begin_nested()
        for date_string in calendar_data.keys():
            python_date = _get_python_date_from_string(date_string)
            python_dow = python_date.weekday()
            try:
                exact_match = True
                for period in defaults_dict[python_dow]:
                    for potential_period in calendar_data[date_string]:
                        match_period = {}
                        match_period['end_minutes'] = potential_period['end_minutes']
                        match_period['start_minutes'] = potential_period['start_minutes']
                        match_period['comments'] = potential_period['comments']

                        # JS gives a "work_units" which is in hours

                        minutes = potential_period['work_units'] * 60
                        work_units_in_quanta = int(minutes / granularity_in_minutes())
                        match_period['work_units_in_quanta'] = work_units_in_quanta

                        # if the period sent in doesn't match the current default then make an exception for it.
                        if not period.match_period(match_period):
                            exact_match = False
                            break

                    # python needs "break 2"
                    if not exact_match:
                        break

                if not exact_match:

                    def sortPeriodDefaults(x,y):
                        return cmp(x.get('start_minutes'),y.get('start_minutes'))

                    # sort periods to ensure all periods are consectutive.
                    calendar_data[date_string].sort(sortPeriodDefaults)

                    # Ensure that all periods are consectutive
                    # ... AND ensure all periods are in quanta bounds
                    check_date = None
                    for aperiod in calendar_data[date_string]:
                        if (aperiod.get('start_minutes') % granularity_in_minutes()) or (aperiod.get('end_minutes') % granularity_in_minutes()):
                            abort(500,"One or more of the time slots is not in half hour increments")

                        if check_date:
                            if check_date != aperiod.get('start_minutes'):
                                abort(500,"One or more of the time slots overlap each other")
                        check_date = aperiod.get('end_minutes')

                    # create all new exceptions
                    for potential_period in calendar_data[date_string]:

                        # Silently ignore zero minute duration periods
                        if potential_period['start_minutes'] == potential_period['end_minutes']:
                            continue

                        new_exception = AvailableExceptions.fromJsDict(calendar_id=calendar_id,
                                exception_date=python_date,
                                start_minutes = potential_period['start_minutes'],
                                end_minutes = potential_period['end_minutes'],
                                work_units = potential_period['work_units'],
                                comments = potential_period['comments'])
                        db_sess.save(new_exception)

            except KeyError:
                db_sess.rollback()
                abort(500, "Invalid date: %s for calendar data." % date_string)
        db_sess.commit()
        # verify the validity of the exceptions just submitted to the database. If the verification raises 
        # return this message back to client.
        try:
            start_python_datetime = datetime(
                python_start_date.year,
                python_start_date.month, 
                python_start_date.day, 0, 0, 0)
            start_normalizer = TimezoneNormalizer(start_python_datetime, cal.timezone)
            start_maintcal_datetime = start_normalizer.get_maintcal_datetime()
            end_python_datetime = datetime(
                python_end_date.year,
                python_end_date.month, 
                python_end_date.day, 0, 0, 0)
            end_normalizer = TimezoneNormalizer(end_python_datetime, cal.timezone)
            end_maintcal_datetime = end_normalizer.get_maintcal_datetime()
            valid = Calculator().verify_times_available([cal.id],start_maintcal_datetime,end_maintcal_datetime) 
        except (InvalidDatetimeException, AmbiguousDatetimeException), e:
            msg, date = e
            abort(400, "A block containing %s date is invalid due to DST. Please either change this block to encompass the entire DST break or remove the block." % date)

        return self.index(calendar_id, date_to_datetime(python_start_date), date_to_datetime(python_end_date))

    def _getStartAndEndMaintcalDatetimes(self,timezone_name):

        # Get input params

        start_year = request.params.get('start_year')
        start_month = request.params.get('start_month')
        start_day = request.params.get('start_day')

        end_year = request.params.get('end_year')
        end_month = request.params.get('end_month')
        end_day = request.params.get('end_day')

        # validate required fields, pylons will automatically validate the id

        if not (start_year and start_month and start_day):
            abort(400, "No start time submitted ('start_year', 'start_month', 'start_day').")

        if not (end_year and end_month and end_day):
            abort(400,"No end times submitted ('end_year','end_month',end_day')")

        # make sure we have valid values to feed into a python datetime for start year, month, and date
        try:
            start_year = int(start_year)
            start_month = int(start_month)
            start_day = int(start_day)
            end_year = int(end_year)
            end_month = int(end_month)
            end_day = int(end_day)

        except ValueError, err:
            abort(400, "Time values must be valid integer representable values; got:\n" + \
                    "start_year: %s\n start_month: %s \n start_day: %s. end_year: %s\n" + \
                    "end_month: %s\n end_day: %s\n" %
                    (start_year, start_month, start_day,end_year,end_month,end_day))

        start_python_datetime = datetime(start_year, start_month, start_day, 0, 0, 0)
        end_python_datetime = datetime(end_year,end_month,end_day,0,0,0)

        if end_python_datetime.date() < start_python_datetime.date():
            abort(400, "End time values must be after start time values")

        return (start_python_datetime, end_python_datetime)

