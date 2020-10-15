import logging
import xmlrpclib
import simplejson
import traceback

from maintcal.lib.base import *
from maintcal.lib.py2extjson import py2extjson
from maintcal.lib import core_xmlrpc
from maintcal.model import db_sess, Server, ScheduledMaintenance, ScheduledService

from authkit.authorize.pylons_adaptors import authorize
from core_authkit.permissions import LoggedIn

log = logging.getLogger(__name__)

class DevicesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('device', 'devices')

    @authorize(LoggedIn())
    def index(self, format='html'):
        """GET /devices: All items in the collection.

        Paging works like this:
            If the results are less than the limit, then this is the last page.

            Example:    If your result size is 100 and your limit is 100, there is another page.
                        If your result size on the next page is then zero, then you are done.

        Sorting:
            Every single field on the computer is a valid sort option.
            But most everything except for computer number is not useful.
        """
        # url_for('devices')
        returned_devices = []
        db_sess.begin_nested()

        if request.params.has_key('account'):
            rpc_args = {'account': int(request.params['account'])}
            if request.params.has_key('page') and \
                request.params.has_key('limit'):
                try:
                    rpc_args['page'] = int(request.params.get('page'))
                    rpc_args['limit'] = int(request.params.get('limit'))
                except ValueError:
                    abort(500,'Got invalid page and or limit arguments for this request')
            try:
                acct_servers = core_xmlrpc.Computer.getServers(**rpc_args)
            except core_xmlrpc.NotAuthenticatedException:
                abort(401, "Please log into CORE")
            except (ValueError,xmlrpclib.Fault):
                log.error("XMLRPC fault while retrieving servers for account %s:\n%s" %
                          (request.params['account'], traceback.format_exc()))
                abort(500,"Could not get devices")
            
            acct_servers_set = [s['server'] for s in acct_servers]
            if not acct_servers_set:
                abort(404,"Account has no devices associated with it.")
            returned_devices = self._updateDeviceCache(acct_servers)

            
        else:
            for s in db_sess.query(Server):
                returned_devices.append(s.toDict())
        
        db_sess.commit()
        if format=='json':
            return py2extjson.dumps(returned_devices)

        return str(returned_devices)
    
    @authorize(LoggedIn())
    def create(self):
        """POST /devices: Create a new item."""
        # url_for('devices')
        pass
    
    @authorize(LoggedIn())
    def new(self, format='html'):
        """GET /devices/new: Form to create a new item."""
        # url_for('new_device')
        pass
    
    @authorize(LoggedIn())
    def update(self, id):
        """PUT /devices/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('device', id=ID),
        #           method='put')
        # url_for('device', id=ID)
        pass

    @authorize(LoggedIn())
    def delete(self, id):
        """DELETE /devices/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('device', id=ID),
        #           method='delete')
        # url_for('device', id=ID)
        pass
    
    @authorize(LoggedIn())
    def show(self, id, format='html'):
        """GET /devices/id: Show a specific item."""
        # url_for('device', id=ID)
        server = db_sess.query(Server).get(id)
        db_sess.begin_nested()
        if not server:
            try:
                c_dict = core_xmlrpc.Computer.getServers(computer=int(id))
                if not c_dict:
                    abort(404, "No such server with id '%s'" % id)
                server = Server.fromDict(c_dict[0])
            except core_xmlrpc.NotAuthenticatedException:
                abort(401, "Please log into CORE")
            except (ValueError, xmlrpclib.Fault):
                abort(404, "No such server with id '%s'" % id)
            db_sess.save(server)
        
        rdict = server.toDict()
        rdict['server_url'] = "%s" % ''.join((config['core.server_url'],
                                                str(rdict['id'])))
        rdict['icon'] = "%s/%s" % (config['core.url'], rdict['icon'])
        db_sess.commit()
        if format == 'json':
            return py2extjson.dumps(rdict)
        return str(rdict)

    @authorize(LoggedIn())
    def shows(self,format='html'):
        """ shows a collection of devices passed as POST arguments """
        if request.method != 'POST':
            abort(405,"This resource only accepts POSTs")

        if request.params.has_key('numbers'):
            requested_devices = [id for id in request.params.getall('numbers') if id]
        else:
            abort(405,"This resource requires an argument of 'numbers'")

        if requested_devices:
            try:
                core_devices = core_xmlrpc.Computer.getServers(
                    computers=requested_devices)
            except core_xmlrpc.NotAuthenticatedException:
                abort(401, "Please log into CORE")
            except (ValueError, xmlrpclib.Fault):
                abort(404,"Could not get devices.")

            if request.params.has_key('has_managed_storage') \
            and request.params['has_managed_storage']:
                managed_storage_servers = []
                for some_dict in core_devices:
                    managed_storage_servers.append(Server.fromDict(some_dict))
                returned_devices = Server.getAttachedDevicesWithManagedStorage(managed_storage_servers)
                # Convert returned_devices into a list of dicts
                device_dicts = [some_server.toDict() for some_server in returned_devices]
                returned_devices = []
                for temp_dict in device_dicts:
                    temp_dict['icon'] = "%s/%s" \
                        % (config['core.url'], temp_dict['icon'])
                    temp_dict['server_url'] = "%s" \
                        % ''.join((config['core.server_url'],str(temp_dict['id'])))
                    returned_devices.append(temp_dict)
            else:
                # if a request has only a single attached device that is not 
                # on the account or is no longer active.
                if core_devices:
                    db_sess.begin_nested()
                    returned_devices = self._updateDeviceCache(core_devices,
                        is_selected=True)
                    db_sess.commit()
                else:
                    # This message only makes sense if lower_bounds status is
                    # working.
                    abort_string = """One or more of the devices attached to 
                                    the selected device is no longer active.
                                    """
                    abort(404,abort_string)
        
        else:
            returned_devices = []
            #abort(400,"No Devices are on this ticket.")
            #servers = db_sess.query(Server).filter('id in (%s)'\
            #% ','.join(request.params.getall('numbers'))).all()
            #
            #returned_devices = [s.toDict() for s in servers]

        if format=='json':
            return py2extjson.dumps(returned_devices)

        return str(returned_devices)
    

    @authorize(LoggedIn())
    def edit(self, id, format='html'):
        """GET /devices/id;edit: Form to edit an existing item."""
        # url_for('edit_device', id=ID)
        pass

    def _updateDeviceCache(self,acct_servers,is_selected=False):
        servs = []
        cached_servers = db_sess.query(Server).filter('id in (%s)'\
            % ','.join([str(s['server']) for s in list(acct_servers)])).all()
        cached_servers_set = [s.id for s in cached_servers]
            
        for acct_server in acct_servers:
            if acct_server['server'] in cached_servers_set:
                for cached_server in cached_servers:
                    if cached_server.id == acct_server['server']:
                        cached_server.updateFromDict(acct_server)
                        server = cached_server
                        break
            else:
                server = Server.fromDict(acct_server)
                cached_servers.append(server)
                db_sess.save(server)
           
            temp_dict = server.toDict()
            temp_dict['attached_devices'] = acct_server['attached_devices']
            temp_dict['icon'] = "%s/%s" \
                % (config['core.url'], temp_dict['icon'])
            temp_dict['server_url'] = "%s" \
                % ''.join((config['core.server_url'],str(temp_dict['id'])))
            if is_selected:
                temp_dict['is_selected'] = True

            servs.append(temp_dict)

        return servs
