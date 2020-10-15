import logging
import simplejson
import urllib
from datetime import date, datetime, timedelta
import time
from pylons import config
import time
import xmlrpclib
import traceback
import pdb

from maintcal.lib.base import *
from maintcal.lib import selector, core_xmlrpc, normalize 
from maintcal.lib.py2extjson import py2extjson
from maintcal.lib.normalize import drop_controls
from maintcal.lib import aggMaintData
from maintcal.lib.maintcal_helpers import updateDeviceCache,NoCOREDevice
from maintcal.model import db_sess,fetchContactId
from maintcal.model import ScheduledMaintenance, ServiceType, Server, ScheduledService, Contact
from maintcal.lib.date import get_database_utc_now
from maintcal.lib.date.maintcal_datetimerange import MaintcalDatetimeRange
from maintcal.lib.date.timezone_renderer import TimezoneRenderer
from maintcal.lib.date.timezone_normalizer import TimezoneNormalizer
from maintcal.lib.date.timezone_normalizer import AmbiguousDatetimeException, InvalidDatetimeException
from maintcal.lib.times_available.calculator import Calculator, HTTP404Error, HTTP400Error

from authkit.authorize.pylons_adaptors import authorize
from core_authkit.permissions import LoggedIn
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime

log = logging.getLogger(__name__)


class MaintenancesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('maintenance', 'maintenances')

    @authorize(LoggedIn())
    def index(self, format='html'):
        """GET /maintenances: All items in the collection."""
        # url_for('maintenances')
        c.maints = db_sess.query(ScheduledMaintenance).order_by(ScheduledMaintenance.id).all()
        return render('/maintenances_index.mako')
    
    @authorize(LoggedIn())
    def create(self):
        """POST /maintenances: Create a new item."""
        # url_for('maintenances')
        db_sess.begin_nested()
        ticket = request.params.get('master_ticket')
        if not ticket:
            abort(400, 'Missing ticket number.')
        maint = ScheduledMaintenance(ticket)
        try:
            core_ticket = core_xmlrpc.Ticket.getTicket(ticket)
        except core_xmlrpc.NotAuthenticatedException:
            abort(401, "Please log into CORE")
        except xmlrpclib.Fault, err:
            log.error("XMLRPC fault while retrieving ticket: %s\n%s" % (ticket,err))
            abort(404,"Could not get ticket information")
        
        maint.account_id = core_ticket.get('account_number')
        maint.account_name = core_ticket.get('account_name')
        maint.general_description = request.params.get('description')
        maint.expedite = normalize.normalize_boolean(request.params.get('expedite'))
        
        add_min = request.params.get('additional_duration_minutes')
        if add_min:
            maint.additional_duration = timedelta(minutes=int(add_min))
        else:
            maint.additional_duration = timedelta(minutes=0)
        
        if request.params.get('service_type_id') == None:
            abort(400, "Missing service type ID")
        try:
            service_type_id = int(request.params.get('service_type_id'))
        except ValueError, e:
            abort(400, "Service type ID is not integer")
        service_type = db_sess.query(ServiceType).get(service_type_id)
        if not service_type:
            abort(400, "Invalid service type id '%s'" % request.params.get('service_type_id'))
        maint.service_type = service_type
        
        # Set the contact ID to the current logged in user
        # use core.user config option if authkit is disabled.
        if not config['use_auth']:
            thisUser = db_sess.query(Contact).get(int(config['core.user_id']))
            if not thisUser:
                thisUser = Contact(int(config['core.user_id']))
                thisUser.username = config['core.user']
                db_sess.save(thisUser)
                log.debug("Contact %d created from (%s,%s)." % (thisUser.id, config.get('core.user_id'), config.get('core.user')))
        else:
            beaker_cache = request.environ['beaker.session'] 
            cid = beaker_cache.get('core.user_id')
            thisUser = db_sess.query(Contact).get(cid)
            if not thisUser:
                thisUser = Contact(cid)
                thisUser.username = beaker_cache.get('core.username')
                db_sess.save(thisUser)
                log.debug("Contact %d created from (%d,%s)." % (thisUser.id, beaker_cache.get('core.user_id'), beaker_cache.get('core.username')))
        maint.contact_id = int(thisUser)
        
        # Servers
        requested_devices = request.params.getall('servers')
        if not requested_devices:
            abort(400, "No servers were selected.")
        # get all devices in local cache.
        try:
            requested_devices = [int(device) for device in requested_devices]
        except ValueError:
            abort(500,"Got invalid requested server number.")

        cached_servers = db_sess.query(Server).filter('id in (%s)'\
        % ','.join([str(s) for s in requested_devices])).all()

        cached_servers_dict = {}
        
        for d in cached_servers:
            cached_servers_dict[d.id] = d 

        ids_only = dict(zip(requested_devices,requested_devices))

        # merge ids and cached devices
        ids_only.update(cached_servers_dict)

        all_devices = ids_only.values()

        # update or create new cached devices as necessary
        try:
            new_servers = updateDeviceCache(all_devices)
        except core_xmlrpc.NotAuthenticatedException:
            abort(401,"Please log into CORE.")

        except NoCOREDevice,e:
            abort(400,e)
            
        # old logic. Nathen Hinson 03/17/09 MCAL-70
        # for s in server_list:
        #     if not s:
        #         abort(400, "No servers were selected.")
        #     serv = db_sess.query(Server).get(s)
        #     if not serv:
        #         try:
        #             serv = Server.fromCore(int(s))
        #             db_sess.save(serv)
        #         except core_xmlrpc.NotAuthenticatedException:
        #             abort(401, "Please log into CORE .")
        #         except ValueError:
        #             abort(400, "Server '%s' not found" % s)
        #     else:
        #         try:
        #             serv.updateFromCore()
        #         except core_xmlrpc.NotAuthenticatedException:
        #             abort(401, "Please log into CORE.")
        #     new_servers.append(serv)
        
        # Call calendar selector
        calendars_dict = selector.select_calendars(new_servers,
                        maintenance_category_id=maint.maintenance_category.id,
                        service_type_id=maint.service_type.id)

        # if the request is being made with calendars use them over 
        # the automatically selected ones. MCAL-17 Nathen Hinson 9-14-2008
        if request.params.has_key('calendars'):
            # if the request has calendars that shouldn't have been 
            # selected append all devices to the service.
            overridden_calendars = request.params.getall('calendars')
            if not overridden_calendars:
                abort(400,"No calendars selected")
            
            cal_ids_added = set(overridden_calendars) - set(calendars_dict.keys())
            cal_ids_removed = set(calendars_dict.keys()) - set(overridden_calendars)
            # remove calendars that have been explicitly removed
            for cal_id in calendars_dict.keys():
                if cal_id in cal_ids_removed:
                    del calendars_dict[cal_id]

            # add calendars that have been added. WARNING: Since there is no
            # logic to determine which devices should be assigned to a service
            # on a calendar that wasn't in the selector, all devices in the 
            # maintenance will appear on that particular service. 
            for cal_id_add in cal_ids_added:
                calendars_dict[cal_id_add] = new_servers
       
        for cal in calendars_dict.keys():
            service = ScheduledService(calendar=cal)
            service.servers=calendars_dict[cal]
            service.maintenance = maint
            db_sess.save(service)
            log.debug("Service created for maintenance %s, calendar %s." % (maint.id, cal))
        db_sess.save(maint)
        db_sess.commit()
        log.debug("Maintenance %s created." % maint.id)
        return simplejson.dumps(self._genCalendarServiceMap(maint))
        #return h.link_to("View maintenances", url=h.url(controller='/maintenances'))

    @authorize(LoggedIn())
    def new(self, format='html'):
        """GET /maintenances/new: Form to create a new item."""
        # url_for('new_maintenance')
        return render('/maintenances_new.mako')

    @authorize(LoggedIn())
    def update(self, id):
        """PUT /maintenances/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('maintenance', id=ID),
        #           method='put')
        # url_for('maintenance', id=ID)
        db_sess.begin_nested()    
        maint = db_sess.query(ScheduledMaintenance).get(id)
        if not maint:
            abort(404, "No such Maintenance with id %s" % id)
        master_ticket = request.params.get('master_ticket')
        description = request.params.get('description')
        expedite_text = request.params.get('expedite')
        additional_minutes = request.params.get('additional_duration_minutes')
        service_type_id = request.params.get('service_type_id')
        contact_name = request.params.get('contact_name')
        
        recreate_services = False
        
        if master_ticket != None and maint.master_ticket != master_ticket :
            maint.master_ticket = master_ticket
        if description != None and maint.general_description != description:
            maint.general_description = description
        if expedite_text != None and maint.expedite != normalize.normalize_boolean(expedite_text):
            maint.expedite = normalize.normalize_boolean(expedite_text)
        if additional_minutes:
            try:
                additional_duration = timedelta(minutes=int(additional_minutes))
                if maint.additional_duration != additional_duration:
                    maint.additional_duration = additional_duration
            except (TypeError, ValueError), err:
                abort(400, "Invalid input for additional minutes: %s" % err)
        if service_type_id != None:
            try:
                if maint.service_type_id != int(service_type_id):
                    maint.service_type = db_sess.query(ServiceType).get(int(service_type_id))
                    recreate_services = True
            except (TypeError, ValueError), err:
                abort(400, 'Invalid input for service type: %s' % err)
        if contact_name != None:
            conts = db_sess.query(Contact).filter_by(username=contact_name).all()
            if conts:
                try:
                    new_cont_id = fetchContactId(contact_name)
                    if maint.contact_id != new_cont_id:
                        maint.contact_id = new_cont_id
                except core_xmlrpc.xmlrpclib.Fault, err:
                    log.error("Error fetching contact info for user '%s':\n%s" % (contact_name, err))
                    abort(500, "There was a problem fetching contact information for user '%s'." % contact_name)

        # recreate services if calendars parameter is passed MCAL-17 
        # Nathen Hinson 09-15-2008
        if request.params.has_key('calendars') and not recreate_services:
            recreate_services = True
        
        server_list = request.params.getall('servers')
        new_servers = []
        if server_list:
            recreate_services = True
            for s in server_list:
                serv = db_sess.query(Server).get(s)
                if not serv:
                    try:
                        serv = Server.fromCore(int(s))
                    except ValueError:
                        abort(400, "Server '%s' not found" % s)
                    except core_xmlrpc.NotAuthenticatedException:
                        abort(401, "Please log into CORE.")
                new_servers.append(serv)
        else:
            new_servers = maint.servers
        
        if recreate_services:
            if maint.state.id != ScheduledMaintenance.State.TEMPORARY:
                abort(400, "Cannot set service type or server list on a server not in 'Temporary' state")
                
            
            # Call calendar selector
            new_calendars_dict = selector.select_calendars(new_servers,
                        maintenance_category_id=maint.maintenance_category.id,
                        service_type_id=maint.service_type.id)
            new_calendars = new_calendars_dict.keys()
            old_calendars = [service.calendar_id for service in maint.services]
            # adjust the new_calendars and old_calendars lists with input from
            # the re-created calendars list
            extra_overrides = []
            if request.params.has_key('calendars'):
                updated_overrides = request.params.getall('calendars')
                try:
                    updated_overrides = [int(o_cal) for o_cal in updated_overrides]
                except:
                    abort(400,"Cannot parse passed calendars")

               # 
               # new_cals_to_remove = set(new_calendars) - set(updated_overrides)
               # old_cals_to_remove = set(old_calendars) - set(updated_overrides)

                #new_calendars = set(new_calendars) - set(updated_overrides)
                #old_calendars = set(old_calendars) - set(updated_overrides)
                
                extra_overrides = set(updated_overrides) - set(new_calendars)

                new_calendars = set(updated_overrides) - extra_overrides

                for cal_id in extra_overrides:
                    new_calendars_dict[cal_id] = new_servers
            
            # add explicit cast to sets in case no calendars param exists
            add_calendars = set(new_calendars) - set(old_calendars)
            del_calendars = set(old_calendars) - set(new_calendars)

            add_calendars = list(add_calendars) + list(extra_overrides)
            #service_list = []
            for service in maint.services:
                if service.calendar_id in del_calendars:
                    db_sess.delete(service) # IS THIS SAFE?? -ejm -- probably Nathen
                else:
                    service.servers = new_calendars_dict[service.calendar.id]
                    #service_list.append(service)
            for cal in add_calendars:
                service = ScheduledService(calendar=cal)
                service.servers = new_calendars_dict[cal]
                service.maintenance = maint
                db_sess.save(service)
                #service_list.append(service)
            #maint.services = service_list
        #db_sess.flush()
        db_sess.commit()
        return simplejson.dumps(self._genCalendarServiceMap(maint))
        #return h.link_to("View this maintenance", url=h.url(controller='/maintenances', action='show', id=id))

    @authorize(LoggedIn())
    def delete(self, id):
        """DELETE /maintenances/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('maintenance', id=ID),
        #           method='delete')
        # url_for('maintenance', id=ID)
        pass

    @authorize(LoggedIn())
    def show(self, id, format='html'):
        """GET /maintenances/id: Show a specific item."""
        # url_for('maintenance', id=ID)
        maint_obj = db_sess.query(ScheduledMaintenance).get(id)
        if not maint_obj:
            abort(404, "No such maintenance with ID %s" % id)

        if format == 'json':
            # this returns just the maintenance
            return simplejson.dumps( maint_obj.toDict(),
                                     sort_keys = True, indent=2)
        if format == 'sjson':
            if not request.params.get('tzname'):
                abort(400, "No timezone information supplied (tzname).")
            timezone_name = urllib.unquote(request.params.get('tzname'))

            # this returns more than the json format,
            # this returns the maintenance AND the services for the maintenance
            rstruct = aggMaintData.do(maint_obj, timezone_name)
            if not rstruct:
                abort(500,"Error aggregating maintenance data with id %s" % id)
            
            return simplejson.dumps(rstruct)

    @authorize(LoggedIn())
    def edit(self, id, format='html'):
        """GET /maintenances/id;edit: Form to edit an existing item."""
        # url_for('edit_maintenance', id=ID)
        c.maint = db_sess.query(ScheduledMaintenance).get(id)
        if not c.maint:
            abort(404, "No such maintenance with ID %s" % id)
        return render('/maintenances_edit.mako')

    @authorize(LoggedIn())
    def ticket(self,id):
        maint_ids = db_sess.query(ScheduledMaintenance).filter_by(
                master_ticket=id).all()
        if maint_ids:
            return simplejson.dumps([maint.id for maint in maint_ids])
        else:
            abort(404,"No Maintenances found associated with ticket: %s" % id)


    @authorize(LoggedIn())
    def durations(self):
        extendedMaintenanceTimes = [
                            {'value':'0','name':'0 min.'},
                            {'value':'30','name':'30 min.'},
                            {'value':'60','name':'1 hour'},
                            {'value':'90','name':'1 hour 30 min.'},
                            {'value':'120','name':'2 hours'},
                            {'value':'150','name':'2 hours 30 min.'},
                            {'value':'180','name':'3 hours'},
                            {'value':'210','name':'3 hours 30 min.'},
                            {'value':'240','name':'4 hours'},
                            {'value':'270','name':'4 hours 30 min.'},
                            {'value':'300','name':'5 hours'}];
        return py2extjson.dumps(extendedMaintenanceTimes)
    



 

    def _makeReturnDict(self, available_times, services, maint_length, timezone_name):
        """
            Make a dictionary of format:
            
                key = day of month
                value = array of:
                            [start_js_time_tuple, end_js_time_tuple]
        """

        return_dict = {}
        return_dict['calendars'] = [{'name':service.calendar.name,
                'value':service.calendar.id} for service in services]

        for python_start_datetime in available_times:

            if python_start_datetime is None:
                abort(500,"No Default Schedule is available"); 

            datetimerange = MaintcalDatetimeRange.from_python_datetimes(
                    python_start_datetime, python_start_datetime + maint_length)

            js_time_tuples = datetimerange.get_javascript_time_tuples(timezone_name)

            day = js_time_tuples[0][2]

            if day not in return_dict:
                return_dict[day] = []

            return_dict[day].append(js_time_tuples)

        return simplejson.dumps(return_dict)

    def _get_end_datetime(self, start_maintcal_datetime):
        """
            Add 5 weeks to the start time. Which is roughly a metric month :) ... or so.
        """
        start_python_datetime = start_maintcal_datetime.to_python_datetime()

        end_python_datetime = start_python_datetime + timedelta(weeks = 5)

        return MaintcalDatetime.from_python_datetime(end_python_datetime)

    def _get_next_quanta_boundary(self, dt):
        # Remove all of the microseconds
        dt = dt.replace(microsecond=0)

        # Make sure that the minutes and seconds are on a quanta boundary

        if (dt.minute == 0) and (dt.second == 0):
            return dt

        if dt.minute < 30:
            return dt.replace(minute=30, second=0)

        if (dt.minute == 30) and (dt.second == 0):
            return dt

        # Advance to the next hour

        dt = dt.replace(minute=0, second=0)
        dt = dt + timedelta(minutes=60)

        return dt

    def _validate_times_available_parms(self, id, params ):

        # Get input params
        start_year = params.get('start_year')
        start_month = params.get('start_month')
        start_day = params.get('start_day')

        end_year = params.get('end_year')
        end_month = params.get('end_month')
        end_day = params.get('end_day')

        if not request.params.get('tzname'):
            raise HTTP400Error("No timezone information supplied (tzname).")
        timezone_name = urllib.unquote(request.params.get('tzname'))

        # validate required fields, pylons will automatically validate the id
        if not (start_year and start_month):
            raise HTTP400Error("No start time submitted ('start_year', 'start_month').")

        # make sure we have valid values to feed into a python datetime for start year, month, and date
        try:
            start_year = int(start_year)
            start_month = int(start_month)
            if start_day != None:
                start_day = int(start_day)
            else:
                start_day = 1
        except ValueError, err:
            raise HTTP404Error("Start time values must be valid integer representable values; got:\n" + \
                    "start_year: %s\n start_month: %s \n start_day: %s." %
                    (start_year, start_month, start_day))

        # Validate that the start date is not before the current datetime 

        start_python_datetime = datetime(start_year, start_month, start_day, 0, 0, 0)
        start_normalizer = TimezoneNormalizer(start_python_datetime, timezone_name)
        start_maintcal_datetime = start_normalizer.get_maintcal_datetime()

        current_maintcal_datetime = get_database_utc_now()


        # If someone asks for a past date, we assume they want the current day
        if start_maintcal_datetime.to_python_datetime() < current_maintcal_datetime.to_python_datetime():
            start = self._get_next_quanta_boundary(current_maintcal_datetime.to_python_datetime())
            start_maintcal_datetime = MaintcalDatetime.from_python_datetime(start)

        # validate the start time is not before the lead time
        maint = db_sess.query(ScheduledMaintenance).get(id)
        if not maint:
            abort(404, "No such maintenance with id '%s'" % id)

        now_plus_lead_time = current_maintcal_datetime.to_python_datetime() + maint.service_type.lead_time

        start_time = start_maintcal_datetime.to_python_datetime()
        if (not maint.expedite) and start_time < now_plus_lead_time:
            start_time = start_time + maint.service_type.lead_time
            start_maintcal_datetime = MaintcalDatetime.from_python_datetime(start_time)

        # End Date validation

        try:
            # Do we have an end date specified?
            # Do we have every field of an end date?
            if end_year and end_month and end_day:

                end_year = int(end_year)
                end_month = int(end_month)
                end_day = int(end_day)

                # create maintcal datetime
                end_python_datetime = datetime(end_year, end_month, end_day, 23, 59, 59)
                end_normalizer = TimezoneNormalizer(end_python_datetime, timezone_name)
                end_maintcal_datetime = end_normalizer.get_maintcal_datetime()

                # Is it greater than the start time? ( this is a sanity check )

                if end_maintcal_datetime.to_python_date() < start_maintcal_datetime.to_python_date():
                    raise HTTP404Error("End time values must be after start time values")

            else:
                # Derive end date

                end_maintcal_datetime = self._get_end_datetime(start_maintcal_datetime)
                
        except (ValueError, AmbiguousDatetimeException, InvalidDatetimeException), e:
            raise HTTP404Error("Invalid End time values; got:\n" + \
                    "end_year: %s\n end_month: %s \n end_day: %s." %
                    end_year, end_month, end_day)

        """
        current_maintcal_datetime = get_database_utc_now()
        current_time = current_maintcal_datetime.to_python_datetime()

        start_datetime = start_maintcal_datetime.to_python_datetime()

        # Handle lead time
        granularity_in_seconds = granularity_in_minutes() * 60

        now_quanta_offset = datetime2timestamp(current_time) % granularity_in_seconds
        gran_interval = timedelta(seconds=granularity_in_seconds)

        if now_quanta_offset > 0:

            something = gran_interval - timedelta(seconds=now_quanta_offset)

            current_time += something

        if start_datetime < current_time:
            start_datetime = current_time
        if not maint.expedite and (start_datetime < current_time + maint.service_type.lead_time):
            start_datetime = current_time + maint.service_type.lead_time
        """

        return (start_maintcal_datetime, end_maintcal_datetime, timezone_name )

    @authorize(LoggedIn())
    def times_available(self, id, format='html'):
        """ Passing in the id of a potential maintenance and get back a list of times 
            available.
           
            We will always require the start year, start month and a start_day.
            We will optionally accept an end year, end month, end day.

            If any component of an end date is specified, all 3 components
            are required.

            Timezone name is required.

            Maintenace id is required.

            Day is optional
                Nate and Ryan have determined the UI should be able to query 
                without needing to know what day it is, requiring a day might break the current UI

        """

        try:
            (start_maintcal_datetime, end_maintcal_datetime, timezone_name ) = self._validate_times_available_parms(id, request.params )

            # At this point, both start_maintcal_datetime and end_maintcal_datetime should be appropriate
            # values when they are converted the original local timezone.

            calculator = Calculator()
            (times_avail, services, maint_length) = calculator.calculate_times_available(
                    id, start_maintcal_datetime, end_maintcal_datetime)

        except HTTP404Error, e:
            abort(404, e)
        except HTTP400Error, e:
            abort(400, e)
        ########## DEBUG ###############
        except IndexError, e:
            log.error(traceback.format_exc())
        ########## DEBUG ###############
        # json-i-fy the result and send to the user
        return self._makeReturnDict(times_avail, services, maint_length, timezone_name)
    
    @authorize(LoggedIn())
    def schedule(self, id):
        db_sess.begin_nested()    
        if not request.method == 'POST':
            return "Must use 'POST'"
        
        posted_contact = request.params.get('contact')
                
        maint = db_sess.query(ScheduledMaintenance).get(id)
        if not maint:
            abort(404, "No such maintenance with id '%s'" % id)

        try:
            start_year = int(request.params.get('start_year'))
            start_month = int(request.params.get('start_month'))
            start_day = int(request.params.get('start_day'))
            start_hour = int(request.params.get('start_hour'))
            start_minute = int(request.params.get('start_minute'))

        except (TypeError,ValueError):
            abort(400,"Missing a complete start time")
        
        #start_time_secs = request.params.get('start_time_seconds')
        #
        #if not start_time_secs:
        #    abort(400, "Missing a start time")

        if not request.params.get('tzname'):
            abort(400, "Missing timezone information ('tzname' field)")

        # an is_dst argument is now a required field.
        try:
            dst_flag = request.params.get('is_dst')
            if not dst_flag:
                abort(400, "Missing Daylight Savings Time information ('is_dst' field)")
            dst_flag = int(dst_flag)
        except ValueError:
            abort(400, "Invalid value for Daylight Savings Time information")

        timezone_name = urllib.unquote(request.params.get('tzname'))

        # just say no to crack
        start_python_datetime = datetime(start_year, start_month, start_day, start_hour, start_minute, 0)

        # accept an optional arugment of is_dst to dis-ambiguate the dst dates
        start_normalizer = TimezoneNormalizer(start_python_datetime, timezone_name,is_dst=dst_flag)

        start_maintcal_datetime = start_normalizer.get_maintcal_datetime()


        start_time = start_maintcal_datetime.to_python_datetime()
        end_time = start_time + (maint.length)

        end_maintcal_datetime = MaintcalDatetime.from_python_datetime(end_time)

        now_maintcal_datetime = get_database_utc_now()

        now_plus_lead_time = now_maintcal_datetime.to_python_datetime() + maint.service_type.lead_time
        if (not maint.expedite) and start_time < now_plus_lead_time:
            abort(400, "%s is before lead time of %s" % (str(start_time), str(maint.service_type.lead_time)))

        # update the contact if necessary
        if posted_contact != None:               
            if posted_contact != str(maint.contact):
                new_contact = db_sess.query(Contact).filter_by(username=posted_contact).all()
                if not new_contact:
                    try:
                        new_contact_id = fetchContactId(posted_contact)
                    except core_xmlrpc.xmlrpclib.Fault, err:
                        log.error("Error fetching contact info for user '%s':\n%s" % (posted_contact, err))
                        abort(500, "There was a problem fetching contact information for user '%s'." % posted_contact)
                else:
                    new_contact_id = new_contact[0].id
                maint.contact_id = new_contact_id
        
         # Update the status of the maintenance
        if maint.state_id == ScheduledMaintenance.State.TEMPORARY:
            maint.request()
        elif maint.state_id == ScheduledMaintenance.State.TENTATIVE and [s for s in maint.services if s.start_time]:
            pass
        else:
            abort(400, 'This maintenance has already been scheduled.')

        for service in maint.services:
            # if user cancels confirm and clicks Schedule, start time is not updated
            if service.start_time:
                break
            cal = service.calendar
                
            # Update the service
            service.start_time = start_time
            service.end_time = end_time
            
        # set the general description text
        maint.general_description = request.params.get('description')

        maint.notify_customer_before        = request.params.get('contactCustomerBefore', False)
        maint.notify_customer_after         = request.params.get('contactCustomerAfter', False) 
        maint.notify_customer_name          = request.params.get('contactCustomerName', u'')
        maint.notify_customer_info          = request.params.get('contactCustomerInfo', u'')
        maint.notify_customer_department    = request.params.get('contactCustomerDepartment', u'')

        #  Validate that the chosen time is still available
        #  NOTE: Lead time has already been accounted for and we can ignore it here 
        #        because it was accounted for in the results given to the user in the GUI
        #
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #  ALSO NOTE: It is technically possible that a race condition can occur and 
        #  two different requests for the same time can perform the calculator step at
        #  exactly the same time, thus both returning success, and then they both commit
        #  causing an overbooking.
        #  It would probably require some sort of explicit table locking in order to prevent
        #  this from occuring.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # This check is being placed right before the actual commit so as to minimize the amount of 
        # time between the calculator getting the data from the database and the commit of this service

        calculator = Calculator()
        (times_avail, services, maint_length) = calculator.calculate_times_available(
            maint.id, start_maintcal_datetime, end_maintcal_datetime, exclude_tentative=True)

        if len(times_avail) == 0:
            abort(409, "The time selected is no longer available, Please click OK and select another time for this maintenance.")
    
        db_sess.commit()
        
        # Update master ticket with private comment
        try:
            ticket_text = """Maintenance has been scheduled, please confirm with all involved groups, contact customer with confirmation, then change status to Subticket Pending."""
            core_xmlrpc.Ticket.addMessage(maint.master_ticket, ticket_text, int(maint.contact or 1), True, False)
        except core_xmlrpc.xmlrpclib.Fault, err:
            log.error("XMLRPC Fault appending message to ticket %s:\n%s" % (maint.master_ticket, err))
        log.debug("Maintenance %s has been scheduled." % maint.id)
        # make a dictionary of calender_ids to service ids.
        cal_id_dict = {}
        for serv in maint.services:
            cal_id_dict[serv.calendar_id] = serv.id
        
        return simplejson.dumps(cal_id_dict)
    
    @authorize(LoggedIn())
    def confirm(self, id):
        if request.method != 'POST':
            abort(400, 'This method accepts only POSTs')
        maint = db_sess.query(ScheduledMaintenance).get(id)
        if not maint:
            abort(404, "No such maintenance with id %s")
        if maint.state_id != ScheduledMaintenance.State.TENTATIVE:
            abort(400, "Maintenance cannot be confirmed in the state it is in now.")
        # Confirm all services
        db_sess.begin_nested()    
        for serv in maint.services:
            serv.schedule()
        maint.schedule()
        db_sess.commit()
        # requery to ensure that the maintenance gets into a scheduled state
        # before attempting to send tickets. MCAL-32. Nathen Hinson 09-11-2008
        maint = db_sess.query(ScheduledMaintenance).get(id)
        if not maint:
            abort(404, "No such maintenance with id %s")
        if maint.state_id != ScheduledMaintenance.State.SCHEDULED:
            abort(400, "Maintenance cannot be confirmed in the state it is in now.")
        else:
            db_sess.begin_nested()    
            self._genServiceTickets(maint)
            db_sess.commit()
        return str(maint.id)

    @authorize(LoggedIn())
    def cancel(self, id):
        db_sess.begin_nested()    
        if request.method != 'POST':
            abort(400, 'This method accepts only POSTs')
        maint = db_sess.query(ScheduledMaintenance).get(id)
        if not maint:
            abort(404, "No such maintenance with id %s")
        if maint.state_id == ScheduledMaintenance.State.COMPLETED:
            abort(400, "Maintenance is already completed and cannot be canceled")
        if maint.state_id == ScheduledMaintenance.State.CANCELED:
            abort(400, "Maintenance is already canceled")
        if request.params.has_key('cancel_message'):
            cancel_message = request.params['cancel_message']
        else:
            cancel_message = None
        
        if config['use_auth']:
            current_contact_id = request.environ['beaker.session'].get('core.user_id')
            is_admin = current_contact_id == maint.contact_id
            if not is_admin:
                for service in maint.services:
                    try:
                        if service.ticket_number:
                            ticket_owner = core_xmlrpc.Ticket.getTicket(service.ticket_number)['assignee_id']
                        else:
                            ticket_owner = None
                        queue_roles = core_xmlrpc.Ticket.getRoles(service.calendar.tckt_queue_id)
                    except core_xmlrpc.xmlrpclib.Fault, err:
                        log.error("XMLRPC fault attempting to fetch ticket permissions: %s" % err)
                        abort(500, "Could not authenticate against CORE.")
                    if 'Admin' in queue_roles:
                        is_admin = True
                        break
                    if ticket_owner and ticket_owner == current_contact_id:
                        is_admin = True
                        break
            if not is_admin:
                abort(403, "User must be an admin of at least one of the associated queues(%s) to edit this maintenance." %
                      ', '.join([service.calendar.name for service in maint.services]))
            current_contact_name = request.environ['beaker.session'].get('core.username')
        else:
            current_contact_id = config['core.user_id']
            current_contact_name = config['core.user']
        
        # Cancel all services
        err_list = []
        for serv in maint.services:
            if serv.state_id != ScheduledService.State.COMPLETED:
                serv.cancel()
                if serv.ticket_number:
                    # add in any cancellation reason
                    if cancel_message:
                        cancel_text = "%s canceled maintenance %d. Reason:\n %s" % (current_contact_name,maint.id,cancel_message)
                    else:
                        cancel_text = "%s canceled maintenance %d." % (current_contact_name,maint.id)
                # Close tickets
                    try:
                        core_xmlrpc.Ticket.addMessage(ticket_number=serv.ticket_number,
                                              body= cancel_text,
                                              contact_id=current_contact_id,
                                              is_private=True,
                                              send_email=False)
                        core_xmlrpc.Ticket.system_updateTicketStatusType(
                            serv.ticket_number,
                            core_xmlrpc.Ticket.STATUS_CONFIRM_SOLVED)
                    except core_xmlrpc.xmlrpclib.Fault, err:
                        log.error("Could not close ticket %s:\n%s" % (serv.ticket_number, err))
                        err_list.append("There was a problem with closing ticket %s" % serv.ticket_number)
        maint.cancel()
        db_sess.commit()
        if err_list:
            return '\n'.join(err_list)
        return str(maint.id)
            
    def _genServiceTickets(self, maint):
        self._addNotifyCustomerTicketComment(maint.master_ticket, maint)
        for service in maint.services:
            if service.ticket_number:
                continue

            # Note: This paragraph of code just produces input for the subject string.
            calendar_timezone_name = service.calendar.timezone or 'UTC'

            timezone_renderer = TimezoneRenderer( calendar_timezone_name )
            result = timezone_renderer.get_javascript_time_tuples( [ service.start_time, service.end_time ] )
            start_python_datetime = datetime(*result[0][0:6])
            end_python_datetime = datetime(*result[1][0:6])

            if service.calendar.timezone and service.calendar.timezone.startswith('US/'):
                timefmt = '%I:%M%p'
            else:
                timefmt = '%H:%M'

            # prepare notes for passing over xml.
            dctrls = drop_controls()
            maint_gen_description = service.maintenance.general_description
            serv_description = service.description
            if maint_gen_description:
                maint_gen_description = maint_gen_description.translate(dctrls)
            if service.description:
                serv_description = serv_description.translate(dctrls)

            subject = "SCHLD %s %s-%s %s: %s - %s" % \
                      (start_python_datetime.strftime('%m/%d'),
                       start_python_datetime.strftime(timefmt),
                       end_python_datetime.strftime(timefmt),
                       calendar_timezone_name,
                       service.maintenance_category.name,
                       service.service_type.name)

            body = """
            A maintenance has been scheduled. Please complete any necessary prep work and change this ticket's status to "Scheduled."
            
            General Description:
            %s
            
            Special Instructions:
            %s
            """ % (maint_gen_description,serv_description)
            try:
                args = [maint.master_ticket, 
                        subject, 
                        body,
                        service.calendar.new_ticket_queue_id]
                # add list of devices for the subticket
                # passing '' as subcategory allows xmlrpc method to change to None.  
                new_ticket_category_id = service.calendar.new_ticket_category_id or ''
                new_ticket_status_id = service.calendar.new_ticket_status_id or ''

                args.extend([1, False, [s.id for s in maint.servers], new_ticket_category_id,new_ticket_status_id, 1])
                ticket_num = core_xmlrpc.Ticket.createSubTicket(*args)
                service.ticket_number = ticket_num
            except xmlrpclib.Fault, err:
                log.error("Error while creating ticket for service %s:\n%s" % (service.id, err))
                abort(500,"Couldn't create ticket")

            self._addNotifyCustomerTicketComment(ticket_num, service.maintenance)

    def _addNotifyCustomerTicketComment(self, ticket_number, maintenance):

        before_and_or_after = ""

        if maintenance.notify_customer_before:
            if maintenance.notify_customer_after:
                before_and_or_after = "before and after the maintenance"
            else:
                before_and_or_after = "before the maintenance"
        else:
            if maintenance.notify_customer_after:
                before_and_or_after = "after the maintenance"
            else:
                # Do not notify the customer 
                return

        if config['use_auth']:
            cache = request.environ.get('beaker.session')
            username = cache.get('core.username')
            user_id = cache.get('core.user_id')
        else:
            username = config['core.user']
            user_id = config['core.user_id']

        notify_customer_department_name = ""

        for service in maintenance.services:
            if maintenance.notify_customer_department:
                if str(maintenance.notify_customer_department) == str(service.calendar.id):
                    notify_customer_department_name = service.calendar.name

        text = """   *** Contact Information entered by: %s ***

The customer should be notified %s using the following information: 
Customer Name: %s
Contact Information: %s
Department that should contact the customer: %s
        """

        text = text % (username, before_and_or_after, maintenance.notify_customer_name, 
                maintenance.notify_customer_info, notify_customer_department_name)

        dctrls = drop_controls()
        text = text.translate(dctrls)

        try:
            core_xmlrpc.Ticket.addMessage(ticket_number=ticket_number,
                                          body=text,
                                          contact_id=user_id,
                                          is_private=True,
                                          send_email=False)
        except core_xmlrpc.xmlrpclib.Fault, err:
            log.error("Could not append notify customer comment to ticket number %s: %s" % (ticket_number, err))

    def _genCalendarServiceMap(self,maint):

        # compose json object with a format of: {'maintenance_id':maint.id,
        # 'calendar_service_map':{<calendar_id>:<service_id>,}}
        rdict = {'maintenance_id':maint.id,'calendar_service_map':{}}
        for service in maint.services:
            rdict['calendar_service_map'][service.calendar_id] = service.id 
        
        return rdict

    @authorize(LoggedIn())
    def set_notify_customer_before_log(self, maintenance_id):
        if not request.params.get('notify_customer_before_log'):
            abort(404,"No parameter given")

        db_sess.begin_nested()    
        maint = db_sess.query(ScheduledMaintenance).get(maintenance_id)
        if not maint:
            abort(404, "No such Maintenance with id %s" % maintenance_id)

        maint.notify_customer_before_log = request.params.get('notify_customer_before_log')
        db_sess.commit()

        if config['use_auth']:
            cache = request.environ.get('beaker.session')
            username = cache.get('core.username')
        else:
            username = config['core.user']

        # Attach ticket comments

        msg = """ *** Notification comment added by: %s ***

The customer has been notified before the maintenance using the following:

%s
"""
        msg = msg % (username, maint.notify_customer_before_log)

        self._attach_private_comment_to_ticket_tree(maint, msg)

    @authorize(LoggedIn())
    def set_notify_customer_after_log(self, maintenance_id):
        if not request.params.get('notify_customer_after_log'):
            abort(404,"No parameter given")

        db_sess.begin_nested()    
        maint = db_sess.query(ScheduledMaintenance).get(maintenance_id)
        if not maint:
            abort(404, "No such Maintenance with id %s" % maintenance_id)

        maint.notify_customer_after_log = request.params.get('notify_customer_after_log')
        db_sess.commit()

        if config['use_auth']:
            cache = request.environ.get('beaker.session')
            username = cache.get('core.username')
        else:
            username = config['core.user']

        # Attach ticket comments

        msg = """ *** Notification comment added by: %s ***

The customer has been notified after the maintenance using the following:

%s
"""
        msg = msg % (username, maint.notify_customer_after_log)

        self._attach_private_comment_to_ticket_tree(maint, msg)

    def _attach_private_comment_to_ticket_tree(self, maintenance, comment):
        """
        Attach a comment to a master ticket and all sub tickets.
        """
        if config['use_auth']:
            cache = request.environ.get('beaker.session')
            user_id = cache.get('core.user_id')
        else:
            user_id = config['core.user_id']

        dctrls = drop_controls()
        formatted_comment = comment.translate(dctrls)

        try:
            core_xmlrpc.Ticket.addMessage(ticket_number=maintenance.master_ticket,
                                          body=formatted_comment,
                                          contact_id=user_id,
                                          is_private=True,
                                          send_email=False)
        except core_xmlrpc.xmlrpclib.Fault, err:
            log.error("Could not append notify customer comment to ticket number %s: %s" % (maintenance.master_ticket, err))

        for service in maintenance.services:
            try:
                core_xmlrpc.Ticket.addMessage(ticket_number=service.ticket_number,
                                              body=formatted_comment,
                                              contact_id=user_id,
                                              is_private=True,
                                              send_email=False)
            except core_xmlrpc.xmlrpclib.Fault, err:
                log.error("Could not append notify customer comment to ticket number %s: %s" % (service.ticket_number, err))

    @authorize(LoggedIn())
    def checkValidUserName(self):
        if not request.params.get('user_string'):
            abort(404,"No parameter given")

        try:
            db_sess.begin_nested()    
            thisId = fetchContactId(request.params.get('user_string'))
            db_sess.commit()
            return str(thisId)
        except:
            log.error("Failure validating user name: %s\n%s" % \
                      (request.params.get('user_string'), traceback.format_exc()))
            abort(404,"Invalid User name %s" % request.params.get('user_string'))
            
