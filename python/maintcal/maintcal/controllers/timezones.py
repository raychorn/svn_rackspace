from datetime import datetime, timedelta
import simplejson
import logging
import urllib
from pylons import config

from maintcal.lib.base import *
from maintcal.lib import json_tz
from maintcal.lib.date.timezone_renderer import TimezoneRenderer
from maintcal.lib.date import get_database_utc_now, seconds_to_hours

log = logging.getLogger(__name__)

class TimezonesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('timzone', 'timezones')


    def index(self, format='html'):
        """GET /timezones: All items in the collection."""
        # url_for('timezones')
        try:
            f_open = open(config['zonenamejs_file'], 'r')
        except IOError:
            json_tz.gen_zonenamesjs()
            try:
                f_open = open(config['zonenamejs_file'], 'r')
            except IOError:
                abort(500, "Could not create zonenames.js")
        
        content = f_open.read()
        try:
            f_open.close()
        except IOError:
            pass # It dun matter; we're leaving anyway
        return content
   
    # TODO: offset() can be optimized by moving the get_database_utc_now() and 
    # .get_javascript_time_tuples() into 1 function in the TimezoneRenderer()
    # that makes only 1 call to the database

    def offset(self):
        """GET /timezones/id: Show a specific item."""
        # url_for('timzone', id=ID)
        
        timezone_name = request.params.get('tzname')
        if not timezone_name:
            abort(400, "Missing 'tzname' argument")

        now_maintcal_datetime = get_database_utc_now()

        try:
            now_time_renderer = TimezoneRenderer(timezone_name)
        except ValueError, e:
            abort(404, "Timezone string is not valid, Got: %s" % timezone_name)

        now_time_tuple = now_time_renderer.get_javascript_time_tuples( [ now_maintcal_datetime ] )
        utc_offset_in_seconds = now_time_tuple[0][6]
        offset_in_hours = seconds_to_hours(utc_offset_in_seconds)

        return simplejson.dumps({'offset_hours':offset_in_hours})

