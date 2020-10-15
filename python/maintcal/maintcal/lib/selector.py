import logging
from sqlalchemy import and_, or_

from maintcal.lib.base import *
from maintcal.model import db_sess, Server, Calendar, Selector, ScheduledMaintenance

log = logging.getLogger(__name__)

def select_calendars(servers, maintenance_category_id=None,service_type_id=None):
    rdict = {}
    #maint = db_sess.query(ScheduledMaintenance).get(maint_id)
    #TODO fill server cache
    #servers = db_sess.query(Server).filter('id in (%s)' % ','.join(str(s) for s in server_list)).all()
    for server in servers:
        additional_cal = []
        cals = db_sess.query(Calendar).\
            filter(Calendar.id == Selector.calendar_id).\
            filter(and_(or_(Selector.segment == server.segment, Selector.segment == None),
                        or_(Selector.category == maintenance_category_id, Selector.category == None),
                        or_(Selector.server_os == server.os_type, Selector.server_os == None),
                        or_(Selector.datacenter == server.datacenter_symbol, Selector.datacenter == None),
                        or_(Selector.has_managed_storage == server.has_managed_storage, Selector.has_managed_storage == None),
                        or_(Selector.managed_storage_type.in_(server.managed_storage_type_list()), Selector.managed_storage_type == None),
                        or_(Selector.has_managed_backup == server.has_managed_backup, Selector.has_managed_backup == None),
                        or_(Selector.is_virtual_machine == server.is_virtual_machine, Selector.is_virtual_machine == None),
                        or_(Selector.is_hypervisor == server.is_hypervisor, Selector.is_hypervisor == None),
                        or_(Selector.is_uk_account == server.is_uk_account, Selector.is_uk_account == None),
                        or_(Selector.has_openstack_role == server.has_openstack_role, Selector.has_openstack_role == None),
                        or_(Selector.service_type_id == service_type_id, Selector.service_type_id == None))).all()
        if server.is_critical_sites_device:
            additional_cal = db_sess.query(Calendar).filter(Calendar.id == Calendar.CRITICAL_SITES).all()                
                
        for cal in cals:
            if rdict.has_key(cal.id):
                rdict[cal.id].append(server)
            else:
                rdict[cal.id] = [server]
        # This hack will check critical sites calendar if device has critical sites sku.
        for cal in additional_cal:
            if rdict.has_key(cal.id):
                rdict[cal.id].append(server)
            else:
                rdict[cal.id] = [server]
    return rdict
