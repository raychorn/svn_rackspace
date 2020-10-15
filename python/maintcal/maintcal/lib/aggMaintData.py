"""
aggregate data from a scheduled maintenance for use in
EXTJS client confirmation dialog.
"""
import logging
import traceback
from datetime import timedelta
from maintcal.model import db_sess, ScheduledMaintenance
from maintcal.lib.date import timedelta2hours
from maintcal.lib.date.timezone_renderer import TimezoneRenderer
from pylons import config

log = logging.getLogger(__name__)

# aggregate maintenance data

def do(maint_obj, timezone_name):
    if not maint_obj:
        return None

    amd = {}
    try:
        amd['maintenance_id'] = maint_obj.id
        amd['maintenance_category'] = str(maint_obj.service_type and maint_obj.service_type.maintenance_category or None)
        amd['service_type'] = str(maint_obj.service_type and maint_obj.service_type.name or None)
        amd['expedite'] = maint_obj.expedite
        amd['additional_duration'] = (maint_obj.additional_duration.seconds or 0)/60 # in minutes
        amd['length'] = timedelta2hours(maint_obj.service_type.length or timedelta(0))
        amd['lead_time'] = timedelta2hours(maint_obj.service_type.lead_time or timedelta(0))

        time_renderer = TimezoneRenderer( timezone_name )

        if maint_obj.services:
            if maint_obj.services[0].start_time:
                amd['start_time_time_tuple'] = time_renderer.get_javascript_time_tuples( [ maint_obj.services[0].start_time ] )[0]

            if maint_obj.services[0].end_time:
                amd['end_time_time_tuple'] = time_renderer.get_javascript_time_tuples( [ maint_obj.services[0].end_time ] )[0]

        amd['devices'] = []
        amd['services'] = []
        amd['contact'] = str(maint_obj.contact or 'None')

        if maint_obj.date_assigned:
            date_assigned_renderer = TimezoneRenderer(timezone_name)
            amd['date_assigned_time_tuple'] = date_assigned_renderer.get_javascript_time_tuples([maint_obj.date_assigned])[0]

        amd['general_description'] = maint_obj.general_description
        amd['service_type_id'] = maint_obj.service_type_id
        amd['master_ticket'] = maint_obj.master_ticket
        amd['account_name'] = maint_obj.account_name
        amd['account_url'] =  ''.join((config['core.account_url'],str(maint_obj.account_id or None)))
        amd['account_id'] = maint_obj.account_id or None
        amd['master_ticket_url'] = ''.join((config['core.ticket_url'],str(maint_obj.master_ticket or None)))
        amd['status_id'] = maint_obj.state.id or 0
        amd['status'] = str(maint_obj.state.name or '')

        notify_customer_department_name = ''
        
        # fill in the devices list
        for service in maint_obj.services:
            if maint_obj.notify_customer_department:
                if str(maint_obj.notify_customer_department) == str(service.calendar.id):
                    notify_customer_department_name = service.calendar.name

            ss = {}
            ss['service_id'] = service.id
            ss['calendar'] = service.calendar and service.calendar.name or ''
            ss['calendar_id'] = service.calendar and service.calendar.id or ''
            ss['ticket_url'] =''.join((config['core.ticket_url'],str(service.ticket_number or '#')))
            ss['ticket'] = service.ticket_number or ''
            ss['description'] = service.description or ''
            ss['status_id'] = service.state.id or 0
            ss['status'] = str(service.state or '')
            amd['services'].append(ss)
            for device in service.servers:
                dd = []
                dd.append(device.id)
                dd.append(''.join((config['core.server_url'],str(device.id))))
                dd.append(''.join((config['core.url'],device.icon or '')))
                dd.append(device.name)
                dd.append(device.os_type)
                if dd not in amd['devices']:
                    amd['devices'].append(dd)

        amd['notify_customer_before']           = maint_obj.notify_customer_before
        amd['notify_customer_after']            = maint_obj.notify_customer_after
        amd['notify_customer_name']             = maint_obj.notify_customer_name
        amd['notify_customer_info']             = maint_obj.notify_customer_info
        amd['notify_customer_department']       = maint_obj.notify_customer_department
        amd['notify_customer_department_name']  = notify_customer_department_name

        return amd

    except:
        print "Exception raised aggregating maintenance %s information:\n%s" %\
                  (maint_obj.id, traceback.format_exc())
        return None

