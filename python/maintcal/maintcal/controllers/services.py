import logging
import simplejson
import urllib
import traceback
from datetime import datetime, timedelta
from sqlalchemy.orm import eagerload

from maintcal.lib.base import *
from maintcal.lib.py2extjson import py2extjson
from maintcal.lib import core_xmlrpc
from maintcal.model import db_sess, ScheduledService, Server

from authkit.authorize.pylons_adaptors import authorize
from core_authkit.permissions import LoggedIn
from maintcal.lib.date.timezone_normalizer import TimezoneNormalizer
log = logging.getLogger(__name__)

class ServicesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('service', 'services')
    
    # Start/end dates for date ranges will be passed in this format
    date_range_format = "%Y%m%d"


    @authorize(LoggedIn())
    def index(self, format='html'):
        """GET /services: All items in the collection."""
        # url_for('services')
        def startTimeSort(a,b):
            return cmp(a['start_time'],b['start_time'])
        if not request.params.has_key('tzname'):
            abort(400, "Please select a tzname.")
        self.timezone_name = urllib.unquote(request.params.get('tzname'))
        services = self._get_services()
        
        contact_id = request.environ['beaker.session'].get('core.user_id')
        
        # add is_admin to both dicts.
        service_info_list = []
        service_info_dict = {}

        # Add the ticket info
        self._add_ticket_info(services)
        
        # get list of ticket numbers and queues

        if config['use_auth'] and format == 'json':
            service_ticket_numbers = []
            service_ticket_queue_ids = []

            for service in services:
                if service.ticket_number:
                    service_ticket_numbers.append(service.ticket_number)
                service_ticket_queue_ids.append(service.calendar.tckt_queue_id)

            # dedupe ticket numbers and queues
            service_ticket_numbers = list(set(service_ticket_numbers))
            service_ticket_queue_ids = list(set(service_ticket_queue_ids))
    
            ticket_assignee_ids = {}
            ticket_roles = {}

            try:
                if service_ticket_numbers:
                    ticket_assignee_ids = core_xmlrpc.Ticket.getAssigneesForTickets(service_ticket_numbers)

                # Grab all of the role information
                for ticket_queue_id in service_ticket_queue_ids:
                    ticket_roles[ticket_queue_id] = core_xmlrpc.Ticket.getRoles(ticket_queue_id)

            except core_xmlrpc.xmlrpclib.Fault, err:
                abort(500, "Error communicating with CORE: %s" % err)
            
        for service in services:
            service_info_dict = service.toDict(timezone_name=self.timezone_name, show_server_info=True)
           
            service_info_dict['is_admin'] = False

            if not config['use_auth']:
                service_info_dict['is_admin'] = True
            elif format == 'json':
                if "Admin" in ticket_roles.setdefault(service.calendar.tckt_queue_id, []):
                    service_info_dict['is_admin'] = True
                elif service.ticket_number:
                    if contact_id == ticket_assignee_ids[service.ticket_number]:
                        service_info_dict['is_admin'] = True

            service_info_list.append(service_info_dict)

        service_info_list.sort(startTimeSort)
        if format=='json':
            return py2extjson.dumps([v for v in service_info_list])
        if format=='sjson':
            rlist = []
            for val in service_info_list:
                sdict = val
                rlist.append((sdict['start_time_time_tuple'],
                              sdict['end_time_time_tuple'],
                              sdict['service_type'],
                              sdict['state_id']))
            return simplejson.dumps(rlist)
        return str([v for v in service_info_list])

    @authorize(LoggedIn())
    def create(self):
        """POST /services: Create a new item."""
        # url_for('services')
        pass

    @authorize(LoggedIn())
    def new(self, format='html'):
        """GET /services/new: Form to create a new item."""
        # url_for('new_service')
        pass

    @authorize(LoggedIn())
    def update(self, id):
        """PUT /services/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('service', id=ID),
        #           method='put')
        # url_for('service', id=ID)
        service = db_sess.query(ScheduledService).get(id)
        if not service:
            abort(404, "No such service with id '%s'" % id)
        
        db_sess.begin_nested()    
        if request.params.get('description'):
            service.description = request.params['description']
        db_sess.commit()

    @authorize(LoggedIn())
    def delete(self, id):
        """DELETE /services/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('service', id=ID),
        #           method='delete')
        # url_for('service', id=ID)
        pass

    @authorize(LoggedIn())
    def show(self, id, format='html'):
        """GET /services/id: Show a specific item."""
        # url_for('service', id=ID)

        if not request.params.has_key('tzname'):
            abort(400, "Please select a tzname.")
            
        self.timezone_name = urllib.unquote(request.params.get('tzname'))

        service = db_sess.query(ScheduledService).get(id)
        if not service:
            abort(404, "No such service with id %s" % id)
        # Add the ticket info
        self._add_ticket_info(service)
        if format == 'json':
            return simplejson.dumps(service.toDict(timezone_name=self.timezone_name, show_server_info=True))
        else:
            return str(service.toDict())

    @authorize(LoggedIn())
    def edit(self, id, format='html'):
        """GET /services/id;edit: Form to edit an existing item."""
        # url_for('edit_service', id=ID)
        pass
    
    @authorize(LoggedIn())
    def cancel(self, id):
        if request.method != 'POST':
            abort(400, 'This method accepts only POSTs')
        service = db_sess.query(ScheduledService).get(id)
        if not service:
            abort(404, "No such service with id %s" % id)
        
        # Check permissions
        if config['use_auth']:
            if not self._check_permissions(service):
                abort(403, "User must be either assigned to the ticket or be an admin of the associated queue (%s) to edit this service." %
                  service.calendar.name)
        
        if service.state_id in (ScheduledService.State.CANCELED,
                                ScheduledService.State.COMPLETED,
                                ScheduledService.State.COMPLETED_WITH_ISSUES,
                                ScheduledService.State.UNSUCCESSFUL):
            abort(400, "Service is not in a state that can be canceled.")
        
        reasons = request.params['reasons']
        if request.params.has_key('cancel_message'):
            service.cancel(reasons, request.params['cancel_message'])
        else:
            service.cancel(reasons)

        maint_cancel = False
        # Close the ticket
        if service.ticket_number:
            if request.params.has_key('cancel_message'):
                cancel_text =  "Canceled service %d with following Reason(s) and Feedback:\n %s \nFeedback:  %s" % (service.id,
                    reasons.replace(',','\n'), request.params['cancel_message'])
            else:
                cancel_text = "canceled maintenance %d with following Reason(s): %s" % (service.id,reasons.replace(',','\n'))

            err_str = self._close_service_ticket(service.ticket_number,cancel_text)
                                            
        else:
            err_str = ''
        # Check the other services on the maintenance and close if it's the last one
        db_sess.begin_nested()    
        if self._is_last_service(service):
            service.maintenance.cancel()
            maint_cancel = True
        db_sess.commit()
        
        if err_str:
            return err_str

        if maint_cancel:
            return simplejson.dumps(
                    {'status_id': service.maintenance.state.id,
                    'status': str(service.maintenance.state),
                    'status_type': 'maintenance'})
        else:
            return simplejson.dumps(
                    {'status_id': service.state.id,
                    'status': str(service.state),
                    'status_type':'service'})
    
    @authorize(LoggedIn())
    def complete(self, id):
        db_sess.begin_nested()    
        if request.method != 'POST':
            abort(400, 'This method accepts only POSTs')
        
        service = db_sess.query(ScheduledService).get(id)
        if not service:
            abort(404, "No such service with id %s" % id)
        
        if config['use_auth']:
            if not self._check_permissions(service):
                abort(403, "User must be an admin of the associated queue (%s) to edit this service." %
                  service.calendar.name)
        
        if service.state_id in (ScheduledService.State.CANCELED,
                                ScheduledService.State.COMPLETED,
                                ScheduledService.State.COMPLETED_WITH_ISSUES,
                                ScheduledService.State.UNSUCCESSFUL):
            abort(400, "Service is not in a state that can be completed.")
        
        maint_complete = False
        # Call complete()
        service.complete()

        # Close the ticket
        if service.ticket_number:
            err_str = self._close_service_ticket(service.ticket_number,
                                             "completed service %d." % service.id)
        else:
            err_str = "This service has no ticket."
        
        # Check the other services on the maintenance and close if it's the last one
        if self._is_last_service(service):
            service.maintenance.complete()
            maint_complete = True
        
        db_sess.commit()
        if err_str:
            return err_str

        if maint_complete:
            return simplejson.dumps(
                    {'status_id': service.maintenance.state.id,
                    'status': str(service.maintenance.state),
                    'status_type': 'maintenance'})
        else:
            return simplejson.dumps(
                    {'status_id': service.state.id,
                    'status': str(service.state),
                    'status_type':'service'})
    
    def _check_permissions(self, service):
        contact_id = request.environ['beaker.session'].get('core.user_id')
        is_admin = contact_id == service.contact_id
        try:
            if service.ticket_number:
                ticket_owner = core_xmlrpc.Ticket.getTicket(service.ticket_number)['assignee_id']
            else:
                ticket_owner = None

            queue_roles = core_xmlrpc.Ticket.getRoles(service.calendar.tckt_queue_id)
        except core_xmlrpc.xmlrpclib.Fault:
            abort(500, "Could not authenticate against CORE.")

        if not is_admin:
            if 'Admin' in queue_roles:
                is_admin = True
        if not is_admin:
            if ticket_owner and contact_id == ticket_owner:
                is_admin = True
        return is_admin
    
    def _is_last_service(self, service):
        maint = service.maintenance
        terminal_states = [ScheduledService.State.COMPLETED, ScheduledService.State.CANCELED, ScheduledService.State.COMPLETED_WITH_ISSUES, ScheduledService.State.UNSUCCESSFUL]
        is_last = True
        for serv in maint.services:
            if not serv.state_id in terminal_states:
                is_last = False
                break
        return is_last
    
    def _close_service_ticket(self, ticket_number, text=None):
        if not text:
            text = "closed the service."
        err_str = ''
        if config['use_auth']:
            cache = request.environ.get('beaker.session')
            username = cache.get('core.username')
            user_id = cache.get('core.user_id')
        else:
            username = config['core.user']
            user_id = config['core.user_id']

        text = "%s %s" % (username, text)
        try:
            core_xmlrpc.Ticket.addMessage(ticket_number=ticket_number,
                                          body=text,
                                          contact_id=user_id,
                                          is_private=True,
                                          send_email=False)
        except core_xmlrpc.xmlrpclib.Fault, err:
            log.error("Could not append comment to ticket number %s: %s" % (ticket_number, err))
            err_str = "There was a problem commenting on ticket number %s." % ticket_number
        
        try:
            core_xmlrpc.Ticket.system_updateTicketStatusType(
                    ticket_number,
                    core_xmlrpc.Ticket.STATUS_CONFIRM_SOLVED)
        except core_xmlrpc.xmlrpclib.Fault, err:
            # Log error
            log.error("Could not close ticket number %s: %s" % (ticket_number, err))
            err_str = "%s\n%s" % (err_str,"There was a problem with closing ticket %s." % ticket_number)
        return err_str


    def _run_service_query(self):
        return db_sess.query(ScheduledService).options(
                eagerload("maintenance"),
                eagerload("servers"),
                eagerload("maintenance.contact"),
                eagerload("maintenance.service_type"),
                eagerload("calendar"))


    def _get_times_for_day(self, start_year, start_month, start_day):
        # get info for one day
        start_python_datetime = datetime(start_year, start_month, start_day)
        start_normalizer = TimezoneNormalizer(start_python_datetime, self.timezone_name)
        start_maintcal_datetime = start_normalizer.get_maintcal_datetime()

        start_time = start_maintcal_datetime.to_python_datetime()
        end_time = start_time + timedelta(days=1)
        return start_time, end_time


    def _get_times_for_month(self, start_year, start_month):
        # get info for one month plus buffer
        buffer_delta = timedelta(7)
        start_python_datetime = datetime(start_year, start_month, 1) - buffer_delta
        start_normalizer = TimezoneNormalizer(start_python_datetime, self.timezone_name)
        start_maintcal_datetime = start_normalizer.get_maintcal_datetime()

        start_time = start_maintcal_datetime.to_python_datetime()

        if start_month == 12:
            end_year = start_year + 1
            end_month = 1
        else:
            end_year = start_year
            end_month = start_month + 1

        end_python_datetime = datetime(end_year, end_month, 1) + buffer_delta
        end_normalizer = TimezoneNormalizer(end_python_datetime, self.timezone_name)
        end_maintcal_datetime = end_normalizer.get_maintcal_datetime()
        end_time = end_maintcal_datetime.to_python_datetime()
        return start_time, end_time


    def _get_times_for_range(self, range_start, range_end):
        def strToDateTime(val):
            """ %Y%m%d format is assumed """
            return datetime(int(val[:4]), int(val[4:6]), int(val[6:8]))
        start_python_datetime = strToDateTime(range_start)
        start_normalizer = TimezoneNormalizer(start_python_datetime, self.timezone_name)
        start_maintcal_datetime = start_normalizer.get_maintcal_datetime()
        start_time = start_maintcal_datetime.to_python_datetime()
        end_python_datetime = strToDateTime(range_end)
        end_normalizer = TimezoneNormalizer(end_python_datetime, self.timezone_name)
        end_maintcal_datetime = end_normalizer.get_maintcal_datetime()
        end_time = end_maintcal_datetime.to_python_datetime()
        return start_time, end_time


    def _filter_for_start_year(self):
        if request.params.get('start_year') is not None:
            try:
                start_year = int(request.params.get('start_year'))
                start_month = int(request.params.get('start_month'))
            except ValueError:
                abort(400, "Please select a valid day to query by.")
            if request.params.get('start_day') is not None:
                try:
                    start_day = int(request.params.get('start_day'))
                except ValueError:
                    abort(400, "Please select a valid day to query by.")
                start_time, end_time = self._get_times_for_day(start_year, start_month, start_day)
            else:
                start_time, end_time = self._get_times_for_month(start_year, start_month)
            self.service_query = self.service_query.filter(ScheduledService.start_time<end_time).\
                    filter(ScheduledService.end_time>start_time)

    
    def _filter_for_date_range(self):
        range_start = request.params.get("range_start")
        range_end = request.params.get("range_end")
        # These params will only appear when filtering for date range. If either (usually both)
        # are missing, no additional filters need to be applied.
        if None not in (range_start, range_end):
            start_time, end_time = self._get_times_for_range(range_start, range_end)
            self.service_query = self.service_query.filter(ScheduledService.start_time<end_time).\
                    filter(ScheduledService.end_time>start_time)

    
    def _filter_on_state(self):
        if request.params.get('states') is not None:
            # decode the URL param
            pre_split = urllib.unquote(request.params.get('states'))
            queryable_hidden_states = 'scheduled_service.state_id not in (%s)' % \
                ','.join(pre_split.split(':'))
            self.service_query = self.service_query.filter(queryable_hidden_states) 


    def _get_services(self):
        self.service_query = self._run_service_query()
        if request.params.get('maintenance') != None:
            self.service_query = self.service_query.filter_by(scheduled_maintenance_id=request.params.get('maintenance'))
        if request.params.get('calendar') != None:
            self.service_query = self.service_query.filter_by(calendar_id=request.params.get('calendar'))
        self._filter_on_state()
        self._filter_for_start_year()
        self._filter_for_date_range()
        return self.service_query.all()


    def _add_ticket_info(self, service_or_services):
        if isinstance(service_or_services, (list, tuple)):
            services = service_or_services
        else:
            services = [service_or_services]
        ticket_numbers = [svc.ticket_number for svc in services
                if svc.ticket_number]
        info = {}
        if ticket_numbers:
            info = core_xmlrpc.Ticket.getInfoForTickets(ticket_numbers)
        for svc in services:
            ticket_info = info.get(svc.ticket_number, {})
            svc.ticket_assignee = ticket_info.get("assignee")
            svc.support_team = ticket_info.get("support_team")

    @authorize(LoggedIn())
    def completeWithIssues(self, id):
        db_sess.begin_nested()    
        if request.method != 'POST':
            abort(400, 'This method accepts only POSTs')
        
        service = db_sess.query(ScheduledService).get(id)
        if not service:
            abort(404, "No such service with id %s" % id)
        
        if config['use_auth']:
            if not self._check_permissions(service):
                abort(403, "User must be an admin of the associated queue (%s) to edit this service." %
                  service.calendar.name)
        
        if service.state_id in (ScheduledService.State.CANCELED,
                                ScheduledService.State.COMPLETED,
                                ScheduledService.State.COMPLETED_WITH_ISSUES,
                                ScheduledService.State.UNSUCCESSFUL):
            abort(400, "Service is not in a state that can be completed.")
        
        maint_complete = False
        # Call complete()
        reasons = request.params['reasons']
        if request.params.has_key('feedback'):
            service.completeWithIssues(reasons, request.params['feedback'])
        else:
            service.completeWithIssues(reasons)

        # Close the ticket
        if service.ticket_number:
            if request.params.has_key('feedback'):
                tckt_msg =  "Completed service %d with following issue(s) and feedback:\n %s \n Feedback: %s" % (service.id,
                    reasons.replace(',','\n'), request.params['feedback'])
            else:
                tckt_msg = "completed service %d with following issue(s) \n%s" % (service.id, reasons.replace(',','\n'))
                                             
            err_str = self._close_service_ticket(service.ticket_number, tckt_msg)

        else:
            err_str = "This service has no ticket."
        
        # Check the other services on the maintenance and close if it's the last one
        if self._is_last_service(service):
            service.maintenance.complete()
            maint_complete = True
        
        db_sess.commit()
        if err_str:
            return err_str

        if maint_complete:
            return simplejson.dumps(
                    {'status_id': service.maintenance.state.id,
                    'status': str(service.maintenance.state),
                    'status_type': 'maintenance'})
        else:
            return simplejson.dumps(
                    {'status_id': service.state.id,
                    'status': str(service.state),
                    'status_type':'service'})
            
    @authorize(LoggedIn())
    def unsuccessful(self, id):
        db_sess.begin_nested()    
        if request.method != 'POST':
            abort(400, 'This method accepts only POSTs')
        
        service = db_sess.query(ScheduledService).get(id)
        if not service:
            abort(404, "No such service with id %s" % id)
        
        if config['use_auth']:
            if not self._check_permissions(service):
                abort(403, "User must be an admin of the associated queue (%s) to edit this service." %
                  service.calendar.name)
        
        if service.state_id in (ScheduledService.State.CANCELED,
                                ScheduledService.State.COMPLETED,
                                ScheduledService.State.COMPLETED_WITH_ISSUES,
                                ScheduledService.State.UNSUCCESSFUL):
            abort(400, "Service is not in a state that can be completed.")
        
        maint_complete = False
        # Call complete()
        reasons = request.params['reasons']
        if request.params.has_key('feedback'):
            service.unsuccessful(reasons, request.params['feedback'])
        else:
            service.unsuccessful(reasons)

        # Close the ticket
        if service.ticket_number:
            if request.params.has_key('feedback'):
                tckt_msg =  "Failed service %d with following issue(s) and feedback:\n %s \n Feedback: %s" % (service.id,
                    reasons.replace(',','\n'), request.params['feedback'])
            else:
                tckt_msg = "Failed service %d with following issue(s) \n%s" % (service.id, reasons.replace(',','\n'))
                                             
            err_str = self._close_service_ticket(service.ticket_number, tckt_msg)

        else:
            err_str = "This service has no ticket."
        
        # Check the other services on the maintenance and close if it's the last one
        if self._is_last_service(service):
            service.maintenance.complete()
            maint_complete = True
        
        db_sess.commit()
        if err_str:
            return err_str

        if maint_complete:
            return simplejson.dumps(
                    {'status_id': service.maintenance.state.id,
                    'status': str(service.maintenance.state),
                    'status_type': 'maintenance'})
        else:
            return simplejson.dumps(
                    {'status_id': service.state.id,
                    'status': str(service.state),
                    'status_type':'service'})
