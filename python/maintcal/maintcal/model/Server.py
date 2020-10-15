from maintcal.lib import core_xmlrpc
from sqlalchemy import and_
import string

import logging

from maintcal.model import db_sess

log = logging.getLogger(__name__)
from maintcal.model.MaintcalModel import MaintcalModel

class Server(MaintcalModel):
    
    def __init__(self, computer_number=0):
        self.id = computer_number
        self.name = u'' 
        self.os_type = u'' 
        self.datacenter_symbol = u''
        self.has_managed_storage = False
        self.managed_storage_type = u'' 
        self.has_managed_backup = False
        self.is_virtual_machine = False
        self.is_hypervisor = False
        self.attached_devices = None
        self.icon = u''
        self.segment = u''
        self.active = True
        self.is_uk_account = False
        self.is_critical_sites_device = False
        self.has_openstack_role = False
    
    @classmethod
    def fromCore(cls, id):
        try:
            c_info = core_xmlrpc.Computer.getServers(computer=int(id))
        except core_xmlrpc.NotAuthenticatedException:
            raise
            #abort(401, "Please log into CORE")
        if not c_info:
            raise ValueError, "No such computer with '%d' listed in CORE"
        c_info = c_info[0]
        return cls.fromDict(c_info)
    
    @classmethod
    def fromDict(cls, server_dict):
        """Creates a server object from a given dictionary"""
        server = cls(server_dict['server'])
        server.updateFromDict(server_dict)
        return server
    
    @classmethod
    def getAttachedDevicesWithManagedStorage(cls, servers):
        all_attached_device_ids = []
        for server in servers:
            attached_device_ids = server.attached_devices_list()
            log.debug("Attached Device Ids: %s For Server Id: %s" % (repr(attached_device_ids), repr(server.id)))
            for device_id in attached_device_ids:
                if device_id is not u'':
                    all_attached_device_ids.append(device_id)
                    
        log.debug("All Attached Device Ids: %s" % repr(all_attached_device_ids))
        Server.updateServerCache(all_attached_device_ids)

        attached_servers = db_sess.query(Server).filter(
                           and_(Server.id.in_(all_attached_device_ids),
                                Server.has_managed_storage == True))
        attached_servers = attached_servers.filter(Server.active == True).all()
        return attached_servers 
    
    @classmethod
    def updateServerCache(cls, server_ids):
        """Update server cache for each server."""
        
        # remove dups
        server_ids = list(set(server_ids))
        log.debug("Updating Server Cache for Server ids: %s" % repr(server_ids))
        
        cache_by_id = dict() 
        cached_servers = db_sess.query(Server).filter(Server.id.in_(server_ids)).all()
         
        already_in_cache = []
        not_in_cache = []

        for server in cached_servers:
            cache_by_id[server.id] = server

        for id in server_ids:
            if int(id) in cache_by_id.keys():
                already_in_cache.append(id)
            else:
                not_in_cache.append(id)
        
        # update stuff already in the cache
        try:
            computer_infos = core_xmlrpc.Computer.getServers(computers=already_in_cache)
            for computer_info in computer_infos:
                for server in cached_servers:
                    if computer_info['server'] == server.id:
                        server.updateFromDict(computer_info)
                        break
                
        except core_xmlrpc.NotAuthenticatedException:
            abort(401, "Please log into CORE.")
      
        # devices in the cache but not reported back from CORE, most likely
        # the device has been taken offline CORE status "Computer No Longer
        # Active". Mark items not returned from computer_infos as active=False
        no_longer_in_cache = [c for c in cache_by_id.keys() if c not in [s['server'] for s in computer_infos]]
        for server_id in no_longer_in_cache:
            for server in cached_servers:
                if server.id == server_id:
                    server.active = False
                    break

        # do updates to db
        if no_longer_in_cache:
            db_sess.flush()
        # insert new stuff into cache
        try:
            computer_infos = core_xmlrpc.Computer.getServers(computers=not_in_cache)
            for computer_info in computer_infos:
                serv = Server.fromDict(computer_info)
                db_sess.save(serv)
        except core_xmlrpc.NotAuthenticatedException:
            abort(401, "Please log into CORE .")
        except ValueError:
            abort(400, "Server '%s' not found" % id)
            
    def updateFromCore(self):
        try:
            c_info = core_xmlrpc.Computer.getServers(computer=self.id)
        except core_xmlrpc.NotAuthenticatedException:
            raise
            #abort(401, "Please log into CORE")
        if not c_info:
            raise ValueError("No such computer with '%d' listed in CORE" % self.id)
        c_info = c_info[0]
        self.updateFromDict(c_info)
    
    def updateFromDict(self, server_dict):
        self.name = server_dict['server_name']
        self.os_type = server_dict['os_group']
        self.datacenter_symbol = server_dict['datacenter']
        self.has_managed_storage = server_dict['has_managed_storage']
        # Normalize a python list into a comma-seperated string 
        if isinstance(server_dict['managed_storage_type'], list):
            self.managed_storage_type = u",".join(map(str, server_dict['managed_storage_type']))
        else:
            self.managed_storage_type = server_dict['managed_storage_type']
        # Normalize a python list into a comma-seperated string 
        if isinstance(server_dict['attached_devices'], list):
            self.attached_devices = u",".join(map(str, server_dict['attached_devices']))
        else:
            self.attached_devices = server_dict['attached_devices']
        self.has_managed_backup = server_dict['has_managed_backup']
        self.is_virtual_machine = server_dict['is_virtual_machine']
        self.is_hypervisor = server_dict['is_hypervisor']
        self.segment = server_dict['segment']
        self.active = True
        self.icon = server_dict['icon']
        self.is_uk_account = server_dict['is_uk_account']
        self.has_openstack_role = server_dict.get('has_openstack_role',False)
        self.is_critical_sites_device = server_dict['is_critical_sites_device']
                                           
    def managed_storage_type_list(self):
        "Return managed_storage_type as a list"
        return string.split(self.managed_storage_type,u',')
    
    def attached_devices_list(self):
        "Return attached_devices as a list"
        return string.split(self.attached_devices,u',')
    
    def toDict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'os' : self.os_type,
            'datacenter' : self.datacenter_symbol,
            'has_managed_storage' : self.has_managed_storage,
            'managed_storage_type' : self.managed_storage_type,
            'has_managed_backup' : self.has_managed_backup,
            'is_virtual_machine' : self.is_virtual_machine,
            'is_hypervisor' : self.is_hypervisor,
            'attached_devices' : self.attached_devices,
            'icon' : self.icon,
            'segment' : self.segment,
            'is_uk_account' : self.is_uk_account,
            'is_critical_sites_device' : self.is_critical_sites_device,
        }
