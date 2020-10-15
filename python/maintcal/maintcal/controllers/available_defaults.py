"""
Conceptually, the user of this controller will not be performing CRUD operations on an individual
available_defaults record.  Instead the user will be updating all of the available_defaults for
a specific calendar and a specific day of the week.

Therefore, there will be only two exposed operations:

index    Display all of the available_times records for a given calendar and a given day of the week.
update   Set all of the available_times records for a given calendar and a given day of the week.

Weekday numbers:

    python date weekday:
        0 = monday
        6 = sunday

    python date isoweekday:
        1 = monday
        7 = sunday

    js weekday:
        0 = sunday
        1 = monday
        6 = saturday

    Database standard for available defaults:
            SAME AS python date weekday:

        0 = monday
        6 = sunday

NOTE: any conversion to and from js_weekday format should occur on the server
      and js should not have to do any conversions!!!

"""
import logging
import simplejson

from maintcal.lib.base import *
from maintcal.lib import core_xmlrpc
from maintcal.model import db_sess, AvailableDefaults, StaleDefaultsException,Calendar
from maintcal.model.AvailableDefaults import ConsecutiveDefaultsException,QuantaBoundsException
from maintcal.lib.py2extjson import py2extjson

from authkit.authorize.pylons_adaptors import authorize
from core_authkit.permissions import LoggedIn

log = logging.getLogger(__name__)

class AvailableDefaultsController(BaseController):

    @authorize(LoggedIn())
    def index(self, calendar_id):
        """
        GET /available_defaults/1
        Returns all available_defaults for a given calendar id.
        """
        results = AvailableDefaults.get_available_defaults_for_calendar(calendar_id)
        r_list = [results]
        return py2extjson.dumps(r_list)


    @authorize(LoggedIn())
    def update(self, calendar_id):
        """
        POST /available_defaults/1/update

        Set all of the available times for a given calendar_id.
        """

        cal = db_sess.query(Calendar).get(calendar_id)

        if not cal:
            abort(400,"Calendar with id: %s not found" % calendar_id)

        if config['use_auth'] and 'Admin' not in core_xmlrpc.Ticket.getRoles(cal.tckt_queue_id):
            abort(403, "User must be admin of associated queue to edit this calendar.")

        calendar_data_json = request.params.get('calendar_data')
        defaults = simplejson.loads(calendar_data_json)
        
        try:
            AvailableDefaults.update_available_defaults_for_calendar(calendar_id, defaults)
        except StaleDefaultsException:
            error_text = "Default Schedule has changed since it was last viewed. Your changes have been discarded." +\
                         " Please reload the application."
            abort(500,error_text)

        except ConsecutiveDefaultsException:
            abort(500,"One or more of the time slots overlap each other")

        except QuantaBoundsException:
            abort(500,"One or more of the time slots is not in half hour increments")

        # code re-use is goooodddd..... guarantee a complete round-trip on save.
        return self.index(calendar_id)
