import logging
import traceback
from xmlrpclib import Fault

from maintcal.lib.base import *
from maintcal.lib import core_xmlrpc
from maintcal.lib.py2extjson import py2extjson

from authkit.authorize.pylons_adaptors import authorize
from core_authkit.permissions import LoggedIn

log = logging.getLogger(__name__)

class XmlrpcproxyController(BaseController):

    interfaces = ['Ticket','Computer','Auth']
    
    @authorize(LoggedIn())
    def index(self,interface_name,method_name):
        # will need to support arguments in the future, right now
        # they are unecessary.
        if interface_name not in self.interfaces:
            abort(404,"Interface Not Found")

        if hasattr(core_xmlrpc.__dict__[interface_name],method_name):
            arg = None
            if request.params.has_key('queue_id'):
                arg = request.params.get('queue_id')
            try:
                requested_data = getattr(core_xmlrpc.__dict__[interface_name],method_name)(args=arg)
            except:
                log.error(traceback.format_exc())
                abort(500,"Error communicating with CORE.")

            return py2extjson.dumps(requested_data,echo_params=request.params)

        else:
            abort(404,"Requested method not found.")
                

