import simplejson
import logging
from datetime import datetime,timedelta
import time
from pylons import config
import traceback

from maintcal.lib.base import *
from maintcal.model import db_sess, Calendar
from maintcal.model import ScheduledService, ServiceType, Server
from maintcal.lib.normalize import normalize_boolean, normalize_interval
from maintcal.lib.py2extjson import py2extjson
from maintcal.lib import core_xmlrpc
from maintcal.lib import selector
from maintcal.lib.date import get_database_utc_now, timedelta2hours

from authkit.authorize.pylons_adaptors import authorize
from authkit.permissions import And
from core_authkit.permissions import LoggedIn, DepartmentIn

log = logging.getLogger(__name__)

class McalendarsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('mcalendar', 'mcalendars')

    @authorize(LoggedIn())
    def index(self, format='html'):    
        """GET /mcalendars: All items in the collection."""
        # url_for('mcalendars')
        # get only active calendars.
        # only returns calendar id, name
        if request.params.has_key('active'):
            cals = db_sess.query(Calendar).filter_by(active=True).all()
        # get all calendars.
        else:
            cals = db_sess.query(Calendar).all()
        if not cals:
            abort(404,"No calendars found")
        cals.sort(lambda x,y: cmp(x.name, y.name))
        if format == 'json':
            return py2extjson.dumps([self._mcalendar_display_values(cal) for cal in cals])        
    
    #@authorize(And(LoggedIn(), DepartmentIn(config['admin_departments'])))
    @authorize(LoggedIn())
    @authorize(DepartmentIn(config['admin_departments']))
    def create(self):
        """POST /mcalendars: Create a new item."""
        # url_for('mcalendars')
        pass

    @authorize(LoggedIn())
    def new(self, format='html'):
        """GET /mcalendars/new: Form to create a new item."""
        # url_for('new_mcalendar')
        pass

    @authorize(LoggedIn())
    def update(self, id):
        """PUT /mcalendars/id: Update an existing item."""
        db_sess.begin_nested()

        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('mcalendar', id=ID),
        #           method='put')
        # url_for('mcalendar', id=ID)
        # values that are valid for editing.

        # Helper to allow a lambda to raise an exception
        def _raise(ex):
            raise ex

        def format_validator_name(f):
            if not f:
                return 'valid'
            names = f.__name__.split('_')
            if len(names) > 1:
                return names[1]

            return names[0]

        def normalize_granularity(val):
            try:
                cal_gran = int(config['calendar_granularity_seconds'])
            except ValueError:
                cal_gran = 1800
            interval = normalize_interval(val)
            if interval.seconds % cal_gran != 0:
                raise ValueError("Value must be in increments of %s seconds" % cal_gran)
            return interval

        validators = {
            'name'                      : str,
            'description'               : str,
            'tckt_queue_id'             : int,
            'active'                    : normalize_boolean,
            'timezone'                  : str,
            'new_ticket_queue_id'       : int,
            'new_ticket_category_id'    : int,
            'new_ticket_status_id'      : int,
            'time_before_ticket_refresh': normalize_granularity,
            'refresh_ticket_assignment' : normalize_boolean,
            'refresh_ticket_queue_id'   : int,
            'refresh_category_id'       : int,
            'refresh_status_id'         : int,
            'hold_tentative_time'       : normalize_granularity 
        }
         
        cal = db_sess.query(Calendar).get(id)
        if not cal:
            abort(400, "No such calendar with id %s" % id)
        
        if config['use_auth'] and 'Admin' not in core_xmlrpc.Ticket.getRoles(cal.tckt_queue_id):
            abort(403, "User must be admin of associated queue to edit this calendar.")

        # Make sure that at least one of the input keys matches a calendar field
        if set(validators.keys()) & set(request.params.keys()):
            pass
        else:
            abort(400,"This resource requires a valid parameter for a calendar update")

        for param in request.params:
            try:
                pvalue = request.params.get(param)
                real_value = validators.get(param,lambda a: _raise(TypeError))(pvalue)
                setattr(cal,param,real_value)
            except (ValueError,TypeError), err:
                log.error("Failed attempt to set %s for calendar %d to %s" % (
                    param, cal.id, request.params.get('new_name')))
                if not validators.get(param):
                    abort(400, "'%s' is not a valid parameter." % param)

                abort(400, "'%s' value should be a %s argument." % (
                    param, format_validator_name(validators.get(param))))
        
        db_sess.commit()
        return str(id)

    @authorize(LoggedIn())
    def delete(self, id):
        """DELETE /mcalendars/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('mcalendar', id=ID),
        #           method='delete')
        # url_for('mcalendar', id=ID)
        pass

    @authorize(LoggedIn())
    def show(self, id, format='html'):
        """GET /mcalendars/id: Show a specific item."""
        # url_for('mcalendar', id=ID)
        cal = db_sess.query(Calendar).get(id)
        if not cal:
            abort(404, "No such calendar with id %s" % id)
        if format == 'json':
            return simplejson.dumps(self._mcalendar_display_values(cal))
        c.mcal_vals = self._mcalendar_display_values(cal)
        return render("/mcalendars_show.mako")

    @authorize(LoggedIn())
    def edit(self, id, format='html'):
        """GET /mcalendars/id;edit: Form to edit an existing item."""
        # url_for('edit_mcalendar', id=ID)
        pass

    def _selector_server_stuff(self):
        # get server objects from passed server ids
        db_sess.begin_nested()
        server_list = request.params.getall('servers')
        if not server_list:
            abort(400, "No devices were selected.")

        # cast returned ids to ints to results from WSGI params and the 
        # db agree in type.
        server_list = [int(i) for i in server_list]

        servers = db_sess.query(Server).filter(
            'id in (%s)' % ','.join(str(s) for s in server_list)).all()

        if len(servers) < 1:
            abort(400, "No valid devices were found.")

        servers_by_id = {}
        managed_storage_servers = []
        for dev in servers:
            servers_by_id[dev.id] = dev
            if dev.has_managed_storage:
                managed_storage_servers.append(dev)
        
        for id in server_list:
            if id in servers_by_id.keys():
                self._update_server_from_core(servers_by_id[id],servers)
            else:
                self._update_server_from_core(id,servers)

        # save any changes
        db_sess.commit()
        return (servers, managed_storage_servers)

    @authorize(LoggedIn())
    def selector(self,format='html'):
        if request.method != 'POST':
            abort(400, 'This method accepts only POSTs')


        # Passing in request.params.get('category_id') is now deprecated,
        # because it always must match the maintenance_category_id of the 
        # given ServiceType.
        # From now on, we will just directly use the maintenance_category_id from the ServiceType.
        if request.params.get('service_id'):
            try:
                service_id = int(request.params.get('service_id'))
                service_type = db_sess.query(ServiceType).get(service_id)
                if not service_type:
                    abort(500,"Invalid Service Type Id")
            except ValueError:
                abort(500, "Service Type Id must be a number.")

            servers, managed_storage_servers = self._selector_server_stuff()

            attached_servers = Server.getAttachedDevicesWithManagedStorage(managed_storage_servers)
            servers.extend(attached_servers)
            
            cals = db_sess.query(Calendar).filter_by(active=True).all()
            selecteds = selector.select_calendars(servers,
                maintenance_category_id=service_type.maintenance_category_id,
                service_type_id=service_type.id)

            if format== 'json':
                return py2extjson.dumps([self._selector_display(cal,isSelected=cal.id in selecteds.keys()) for cal in cals])
            else:
                return str([self._selector_display(cal,isSelected=cal.id in selecteds.keys()) for cal in cals])

        else:
            # Why do we bother doing anything aside from just returning an error here ?!?!?!?!?!?
            # Why don't we just abort 400 or abort 404 here???
            self._selector_server_stuff()
            cals = db_sess.query(Calendar).filter_by(active=True).all()
            if format == 'json':
                return py2extjson.dumps([self._selector_display(cal,isError=True) for cal in cals]) 
            else:
                return str([self._selector_display(cal,isError=True) for cal in cals])
                
    @authorize(LoggedIn())
    def show_calendar_info(self, format='html'):
        if request.method != 'POST':
            abort(400, 'This method accepts only POSTs')            
        
        admin_console = ('admin_console' in request.params)
        allData = ('allData' in request.params)
        calendars = request.params.get('calendars',None)

        try:
            if calendars:
                cals = [db_sess.query(Calendar).get(int(calendars))]
            else:
                cals = db_sess.query(Calendar).all()
        except ValueError:
            abort(400, "Invalid Calendar id: %s" % (calendars))

        if not cals or (cals == [None]):
            abort(404,"No calendars found")
        if format == 'json':
            return py2extjson.dumps(dict(tuple([(cal.id,self._mcalendar_display_values(cal, admin_console, allData)) for cal in cals])))
        else:
            return str([self._mcalendar_display_values(cal, admin_console, allData) for cal in cals])

    def _selector_display(self,cal,isSelected=False,isError=False):
        # isError is true if no default calendars were selected
        return {
            'id' : cal.id,
            'name' : cal.name,
            'description' : cal.description,
            'is_selected' : isSelected,
            'is_error' : isError
        }

    def _update_server_from_core(self,dev,cached_server_list):
        if not isinstance(dev,Server):
            try:
                serv = Server.fromCore(int(dev))
                db_sess.save(serv)
                cached_server_list.append(serv)
            except core_xmlrpc.NotAuthenticatedException:
                abort(401, "Please log into CORE .")
            except ValueError:
                abort(400, "Server '%s' not found" % dev)
        else:
            try:
                dev.updateFromCore()
            except core_xmlrpc.NotAuthenticatedException:
                abort(401, "Please log into CORE.")
    
    def _mcalendar_display_values(self, cal, admin_console=False, allData=False):                   
        if config['use_auth']:
            is_admin = 'Admin' in core_xmlrpc.Ticket.getRoles(cal.tckt_queue_id)
        else:
            is_admin = True
        if admin_console:
            if allData:
                if not cal.time_before_ticket_refresh:
                    time_before_ticket_refresh = 0
                else:
                    time_before_ticket_refresh = float(timedelta2hours(cal.time_before_ticket_refresh))                
                if not cal.hold_tentative_time:
                    hold_tentative_time = 0
                else:
                    hold_tentative_time = float(timedelta2hours(cal.hold_tentative_time))
                return {
                    'id' : cal.id,
                    'name' : cal.name,
                    'description' : cal.description,
                    'active' : cal.active,
                    'tckt_queue_id' : cal.tckt_queue_id,
                    'timezone' : cal.timezone,
                    'is_admin' : is_admin,
                    'available_states' : ScheduledService.State.state_names,
                    'new_ticket_queue_id' : cal.new_ticket_queue_id,
                    'new_ticket_category_id' : cal.new_ticket_category_id,
                    'new_ticket_status_id' : cal.new_ticket_status_id,
                    'time_before_ticket_refresh' : time_before_ticket_refresh,
                    'refresh_ticket_assignment' : cal.refresh_ticket_assignment,
                    'refresh_ticket_queue_id' : cal.refresh_ticket_queue_id,
                    'refresh_category_id' : cal.refresh_category_id,
                    'refresh_status_id' : cal.refresh_status_id,
                    'hold_tentative_time' : hold_tentative_time
                }            
            else:
                return {
                    'id' : cal.id,
                    'name' : cal.name   
                }    
        else:
            return {
                'id' : cal.id,
                'name' : cal.name,
                'description' : cal.description,
                'active' : cal.active,
                'tckt_queue_id' : cal.tckt_queue_id,
                'is_admin' : is_admin,
                'available_states' : ScheduledService.State.state_names
            }
