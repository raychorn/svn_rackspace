from pylons import config, request
import xmlrpclib
from xmlrpclib import Fault
import logging
log = logging.getLogger(__name__)

#from maintcal.model import fetchContactId, fetchContactUserName

class NotAuthenticatedException(Exception):
    pass

class RequiredArgument(Exception): pass

def get_core_user():
    auth_module = xmlrpclib.Server("%s/Auth" % config['core.xmlrpc_url'])
    if config.get('core.user'):
        # Development purposes only!
        core_user = config['core.user']
    else:
        token = request.cookies.get(config['core.cookie_name'])
        if not token:
            raise NotAuthenticatedException
        try:
            beaker_cache = request.environ.get('beaker.session')
            if not beaker_cache.get('core.user_id'):
                beaker_cache['core.user_id'] = auth_module.getContactID(token)
            if not beaker_cache.get('core.username'):
                beaker_cache['core.username'] = auth_module.getUsername(token)
            core_user = beaker_cache.get('core.user_id')
        except xmlrpclib.Fault, err:
            log.error("Could not populate beaker session information for:\nUser ID:%s\nUserName:%s" %
                      (beaker_cache.get('core.user_id'),beaker_cache.get('core.username')))
    return core_user
 
#TODO Use CORE token instead
def get_auth_token():
    auth_module = xmlrpclib.Server("%s/Auth" % config['core.xmlrpc_url'])
    if config.get('core.user'):
        # Development purposes only!
        core_user = config['core.user']
        core_password = config.get('core.user_password')
        try:
            token = auth_module.userLogin(core_user, core_password)
        except xmlrpclib.Fault, err:
            log.error("Could not retrieve authentication token from CORE:\n%s" %
                      (err))
    else:
        token = request.cookies.get(config['core.cookie_name'])
        if not token:
            raise NotAuthenticatedException
    beaker_cache = request.environ.get('beaker.session')
    if not beaker_cache.get('core.token'):
        beaker_cache['core.token'] = token
    try:
        if not beaker_cache.get('core.user_id'):
            beaker_cache['core.user_id'] = auth_module.getContactID(token)
        if not beaker_cache.get('core.username'):
            beaker_cache['core.username'] = auth_module.getUsername(token)
    except xmlrpclib.Fault, err:
        log.error("Could not populate beaker session information for:\nUser ID:%s\nUserName:%s" %
                  (beaker_cache.get('core.user_id'),beaker_cache.get('core.username')))
    return token

class Auth(object):
    @classmethod
    def getContactId(cls, user_name):
        core_auth = xmlrpclib.Server("%s/Auth" % config['core.xmlrpc_url'])
        return core_auth.getInfoFromUserName(user_name)['contact_id']
    
    @classmethod
    def getUserName(cls, contact_id):
        core_auth = xmlrpclib.Server("%s/Auth" % config['core.xmlrpc_url'])
        return core_auth.getInfoFromContactId(contact_id)['user_name']
    
class Computer(object):
    @classmethod
    def getServers(cls, **kw):
        core_computer = xmlrpclib.Server("%s/Computer/::session_id::%s" % (config.get('core.xmlrpc_url'), get_auth_token()))
        # lower_bound_status = 1
        kw['lower_bound_status'] = 1
        if 'account' in kw.keys():
            # ensure all arguments are int values
            if [arg for arg in kw.values() if not isinstance(arg,int)]:
            #if not isinstance(kw['account'], int):
                raise TypeError, "'account' keyword must be an integer"
            kw['account'] = [kw['account']]
            if 'page' in kw.keys():
                return core_computer.getDetailsByAccounts(kw['account'],
                    kw['lower_bound_status'],kw['page'],kw['limit'])
            else:
                 return core_computer.getDetailsByAccounts(kw['account'],
                    kw['lower_bound_status'])
        if 'accounts' in kw.keys():
            if not isinstance(kw['accounts'], list):
                raise TypeError, "'accounts' keyword must be a list of integers"
            if 'page' in kw.keys():
                return core_computer.getDetailsByAccounts(kw['accounts'],
                    kw['lower_bound_status'],kw['page'],kw['limit'])
            else:
                 return core_computer.getDetailsByAccounts(kw['accounts'],
                    kw['lower_bound_status'])
        if 'computer' in kw.keys():
            if not isinstance(kw['computer'], int):
                raise TypeError, "'computer' keyword must be an integer"
            return core_computer.getDetailsByComputers([kw['computer']], kw['lower_bound_status'])
        if 'computers' in kw.keys():
            if not isinstance(kw['computers'], list):
                raise TypeError, "'computers' keyword must be a list of integers"
            if len(kw['computers']):
                return core_computer.getDetailsByComputers(kw['computers'], kw['lower_bound_status'])
            else:
                return []
        return None

class Ticket(object):
    
    STATUS_SOLVED = 19
    STATUS_CONFIRM_SOLVED=26
    
    @classmethod
    def _core_ticket(cls):
        return xmlrpclib.Server("%s/Ticket/::session_id::%s" % (config.get('core.xmlrpc_url'), get_auth_token()))

    @classmethod
    def getTicket(cls, ticket_number):
        return cls._core_ticket().getTicketInfo(ticket_number)

    @classmethod
    def getAssigneesForTickets(cls, ticket_numbers):
        return cls._core_ticket().getAssigneesForTickets(ticket_numbers)
    
    @classmethod
    def getInfoForTickets(cls, ticket_list):
        return cls._core_ticket().getInfoForTickets(ticket_list)
    
    @classmethod
    def getActorsOnTicket(cls, ticket_number):
        return cls._core_ticket().getActorsOnTicket(ticket_number)
    
    @classmethod
    def assignTicket(cls, ticket_number, assignee):
        return cls._core_ticket().assignTicket(ticket_number, assignee)
    
    @classmethod
    def getRoles(cls, queue_number):
        return cls._core_ticket().getQueueRoles(queue_number)
    
    @classmethod
    def createSubTicket(cls, *args):
        return cls._core_ticket().createSubTicket(*args)

    @classmethod
    def addMessage(cls, ticket_number, body, contact_id, is_private, send_email):
        return cls._core_ticket().addMessage(ticket_number, body, contact_id, is_private, send_email)

    @classmethod
    def getQueues(cls,args=None):
        return cls._core_ticket().getQueues()

    @classmethod
    def system_getQueueSubCategories(cls,args=None):
        if not args:
            raise RequiredArguments
        return System.run('Ticket','getQueueSubCategories',args)

    @classmethod
    def system_getStatuses(cls,args=None):
        if not args:
            raise RequiredArguments
        return System.run('Ticket','getStatusesForQueue',args)
    
    @classmethod
    def system_getTicketsStatusTypes(cls, ticket_numbers):
        return System.run('Ticket', 'getTicketsStatusTypes', ticket_numbers)
    
    @classmethod
    def system_updateTicketStatusType(cls, ticket_number, status_type, unassign=True):
        return System.run('Ticket', 'updateTicketStatusType', ticket_number, status_type, unassign)
    
    @classmethod
    def system_updateTicketAttributes(cls, ticket_number, queue, category, status_type, unassign=True):
        return System.run('Ticket', 'updateTicketAttributes', ticket_number, queue, category, status_type, unassign)
    
class System(object):
    
    @classmethod
    def run(cls, module, method, *args, **kwargs):
        core_system = xmlrpclib.Server("%s/System/" % (config.get('core.xmlrpc_url')))
        key = config.get('core.system_user_key')
        log.error("%s %s - called." % (module, method))
        return core_system.run(key, module, method, *args, **kwargs)
