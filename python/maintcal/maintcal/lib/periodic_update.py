import logging
import datetime
import traceback
from xmlrpclib import Fault
from pylons import config

from maintcal.lib import core_xmlrpc
from maintcal.model import db_sess, ScheduledService, ScheduledMaintenance,Calendar
#from maintcal.lib.base import *

log = logging.getLogger(__name__)

class PeriodicUpdate(object):
    
    STATUS_NEW = 1
    STATUS_SCHEDULED = 23
    STATUS_DEFAULT_TERMINAL = 3
    STATUS_TERMINAL = 7
    STATUS_SOLVED = 19
    STATUS_CONFIRM_SOLVED = 26
    
    #CLOSED_STATUSES = [STATUS_TERMINAL, STATUS_SOLVED, STATUS_CONFIRM_SOLVED]
    CLOSED_STATUSES = ["Confirm Solved", "Solved", "Terminal"]
    @classmethod
    def run_all(cls):
        try:
            cls.update_tickets()
        except Exception, err:
            log.error("[REAPER] UpdateTickets failed: %s" % err)
            db_sess.remove()
        try:
            cls.stale_maintenance_cleanup()
        except Exception, err:
            log.error("[REAPER] StaleMaintenanceCleanup failed: %s\n%s" % (err,traceback.format_exc()))
            db_sess.remove()
        try:
            cls.expire_past_due_services()
        except:
            log.error("[REAPER] ExpirePastDueServcies failed: %s" % err)
            db_sess.remove()
        db_sess.remove()
    
    @classmethod
    def update_tickets(cls):
        """Update tickets for services that are beginning at a Calendar's
           time_before_ticket_refresh value.
        """
        # MCAL-78: Admin console, time to refresh tickets and unassign them
        # or not is now based on calendar configuration.
        #MCAL-35 added unassign variable to ticket to not unassign ticket on update
        #unassign=False
        # the 'nested-ness' of this should be ignored if the transaction is top-level
        #db_sess.begin()
        due_services = db_sess.query(ScheduledService).\
            filter(ScheduledService.calendar_id == Calendar.id).\
            filter(ScheduledService.ticket_number != None).\
            filter(ScheduledService.ticket_popped == False).\
            filter(ScheduledService.state_id == ScheduledService.State.SCHEDULED)
        due_services = due_services.filter("start_time >= now() at time zone 'UTC'")
        due_services = due_services.filter("start_time <= now() at time zone 'UTC' + time_before_ticket_refresh")

        due_services = due_services.all()
        ticket_list = []
        for service in due_services:
            if service.ticket_number:
                ticket_list.append(service.ticket_number)
        ticket_status_types = core_xmlrpc.Ticket.system_getTicketsStatusTypes(ticket_list)
        new_ticket_list = []
        for service in due_services:
            if ticket_status_types.has_key(service.ticket_number) and \
              not (set(cls.CLOSED_STATUSES) & set(ticket_status_types[service.ticket_number])):
                try:
                    core_xmlrpc.Ticket.system_updateTicketAttributes(
                        service.ticket_number, 
                        service.calendar.refresh_ticket_queue_id or '', 
                        service.calendar.refresh_category_id or '',
                        service.calendar.refresh_status_id or cls.STATUS_NEW, 
                        service.calendar.refresh_ticket_assignment)
                    service.ticket_popped = True
                    new_ticket_list.append(service.ticket_number)
                except Fault:
                    log.error(str(traceback.format_exc()))
                    continue
        log.info("[REAPER] Tickets %s were refreshed." % ",".join(new_ticket_list))
        # rollback causes this session to go into an inconsistent state with 
        # SQLAlchemy 0.4.6.
        #db_sess.rollback()
        db_sess.commit()
    

    @classmethod
    def stale_maintenance_cleanup(cls):
        """This cancels all stale maintenances and returns a list of the ids
        of the maintenances that were just canceled."""
        return ScheduledMaintenance.find_and_call('stale_maintenances', 'cancel')


    @classmethod
    def expire_past_due_services(cls):
        """Expire any services that should have already been performed by now, but wasn't."""
        return ScheduledService.find_and_call('past_due_services', 'expire')
