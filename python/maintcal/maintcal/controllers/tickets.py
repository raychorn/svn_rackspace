import logging
from xmlrpclib import Fault

from maintcal.lib.base import *
from maintcal.lib import core_xmlrpc
from maintcal.lib.py2extjson import py2extjson

from authkit.authorize.pylons_adaptors import authorize
from core_authkit.permissions import LoggedIn
from maintcal.model import db_sess, ScheduledMaintenance, ScheduledService

from pylons import config

log = logging.getLogger(__name__)

class TicketsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('ticket', 'tickets')

    @authorize(LoggedIn())
    def index(self, format='html'):
        """GET /tickets: All items in the collection."""
        # url_for('tickets')
        pass
    
    @authorize(LoggedIn())
    def create(self):
        """POST /tickets: Create a new item."""
        # url_for('tickets')
        pass
    
    @authorize(LoggedIn())
    def new(self, format='html'):
        """GET /tickets/new: Form to create a new item."""
        # url_for('new_ticket')
        pass

    @authorize(LoggedIn())
    def update(self, id):
        """PUT /tickets/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('ticket', id=ID),
        #           method='put')
        # url_for('ticket', id=ID)
        pass

    @authorize(LoggedIn())
    def delete(self, id):
        """DELETE /tickets/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('ticket', id=ID),
        #           method='delete')
        # url_for('ticket', id=ID)
        pass

    @authorize(LoggedIn())
    def show(self, id, format='html'):
        """GET /tickets/id: Show a specific item."""
        # url_for('ticket', id=ID)
        try:
            ticket_info = core_xmlrpc.Ticket.getTicket(id)
        except core_xmlrpc.NotAuthenticatedException:
                abort(401, "Please log into CORE")
        beaker_cache = request.environ['beaker.session']
        ticket_info['contact'] = beaker_cache.get('core.username')
        ticket_info['account_url'] = '%s%s' % (config['core.account_url'], ticket_info['account_number'])
        ticket_info['ticket_url'] = '%s%s' % (config['core.ticket_url'], ticket_info['ticket_number'])
        ticket_info['notify_statuses'] = self.get_notify_statuses()

        if format=='json':
            return py2extjson.dumps(ticket_info)
        return str(ticket_info)
    
    @authorize(LoggedIn())
    def edit(self, id, format='html'):
        """GET /tickets/id;edit: Form to edit an existing item."""
        # url_for('edit_ticket', id=ID)
        pass
    
    @authorize(LoggedIn())
    def info(self, id):
        # TODO: remove this method after core CPT has switched to only
        #       using info_json
        #       Then we can also remove the related mako template.
        return self.get_info(id, 'html')

    @authorize(LoggedIn())
    def info_json(self, id):
        """ I have defined this property instead of using a format string
            in the route because we are currently using map.resource and
            I am not sure how to specify the format. """
        return self.get_info(id, 'json')

    def get_info(self, id, format='html'):
        # ID number is the ticket number in this case
        servs = db_sess.query(ScheduledService).filter_by(ticket_number=id).all()
        existing_maint_ids = [str(serv.maintenance.id) for serv in servs]
        maints = db_sess.query(ScheduledMaintenance).filter_by(master_ticket=id)
        if existing_maint_ids:
            maints = maints.filter('id not in (%s)' % ','.join(existing_maint_ids))
        maints = maints.all()
        if not maints and not servs:
            return 'No maintenance information for this ticket'
        c.maintenances = maints
        c.services = servs

        if format != 'json':
            return render('/tickets_info.mako')
        
        # Return the data as json

        out = {}
        out['maintenances'] = []
        out['services'] = []

        for maint in c.maintenances:
            out['maintenances'].append({
                'maintenance_id':         str(maint.id),
                'maintenance_category':   str(maint.maintenance_category),
                'service_type':           str(maint.service_type),
                'maintenance_state':      str(maint.state)})

        for serv in c.services:
            out['services'].append({
                'maintenance_id':         str(serv.maintenance.id),
                'maintenance_category':   str(serv.maintenance.maintenance_category),
                'service_type':           str(serv.maintenance.service_type),
                'maintenance_state':      str(serv.maintenance.state),
                'service_id':             str(serv.id),
                'service_calendar':       str(serv.calendar),
                'service_state':          str(serv.state)})

        return py2extjson.dumps(out)

    def _build_cookie_string(self, username, token):
        cookie_string = "COOKIE_last_login=%s; redacted_admin_session=%s;" % (username, token)
        return cookie_string

    def get_notify_statuses(self, format='json'):
        """
        Call out to core to retrieve a list of queue ids that have
        an 'In Progress' status.

        key:    queue_id
        value:  status_id for 'In Progress' status
        """
        import urllib2
        import simplejson
        from maintcal.model import Calendar
        import os

        # check to see if the https_proxy env var is set and loose it.
        # It breaks urllib2 in python2.4
        if os.environ.get('https_proxy', None):
            del os.environ['https_proxy']

        core_user = core_xmlrpc.get_core_user()

        notify_queues_url = '%s/py/ticket/maintcal_notify_queues.pt' % config['core.url']

        auth_token = core_xmlrpc.get_auth_token()
        cookie_string = self._build_cookie_string(core_user, auth_token)

        req = urllib2.Request(notify_queues_url)
        req.add_header("Cookie", cookie_string)

        response    = urllib2.urlopen(req)
        json_data   = response.read()
        raw_data    = simplejson.loads(json_data)

        #   Convert the keys from tckt_queue_id to calendar_id
        cals = db_sess.query(Calendar).filter_by(active=True).all()
        
        converted_data = {}
        for tckt_queue_id, status_id in raw_data.items():
            for cal in cals:
                #   We must cast to str to avoid unicode values not matching 
                if str(cal.tckt_queue_id) == str(tckt_queue_id):
                    converted_data[cal.id] = status_id

        return converted_data

    @authorize(LoggedIn())
    def actors_on_ticket(self, id):
        actors = core_xmlrpc.Ticket.getActorsOnTicket(id)
        return py2extjson.dumps(actors)


    @authorize(LoggedIn())
    def assign(self, ticket, id):
        # Check for 'assign to self'
        if id == "self":
            id = request.cookies.get("COOKIE_last_login")
        try:
            ret = core_xmlrpc.Ticket.assignTicket(ticket, id)
        except Fault, e:
            abort(e.faultCode, e.faultString)
        return ret

