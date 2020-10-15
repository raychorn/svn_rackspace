from maintcal.tests.lib import url_for, MaintcalFunctionalTest

from mocker import Mocker, ANY
from datetime import datetime
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import select,label,func

from maintcal.model import db_sess, ScheduledService, ScheduledMaintenance
from maintcal.model.tables import scheduled_service_table
from maintcal.lib import core_xmlrpc
from maintcal.lib import periodic_update

class TestPeriodicUpdate(MaintcalFunctionalTest):
    def local_setup(self):
        #self.mocker = Mocker()
        #fake_date = self.mocker.replace(datetime)
        #fake_date.now(ANY)
        #self.mocker.result(datetime(2008, 1, 8, 9,45))
        #self.mocker.count(0,5)
        #fake_xmlrpc_ticket = self.mocker.replace(core_xmlrpc.Ticket)
        #fake_xmlrpc_ticket.system_getTicketsStatusTypes(ANY)
        #self.mocker.result({'080112-05000': [23]})
        ##self.mocker.count(1,1)
        ##fake_xmlrpc_ticket2 = self.mocker.replace(core_xmlrpc.Ticket)
        #fake_xmlrpc_ticket.system_updateTicketStatusType('080112-05000', 1)
        #self.mocker.result(1234)
        #self.mocker.count(1,1)
        #self.mocker.replay()
        pass
 
    def testUpdateTickets(self):
        mocker = Mocker()
        fake_date = mocker.replace(datetime)
        fake_date.now(ANY)
        mocker.result(datetime(2008, 1, 8, 9,45))
        mocker.count(1,1)
        fake_xmlrpc_ticket = mocker.replace(core_xmlrpc.Ticket)
        fake_xmlrpc_ticket.system_getTicketsStatusTypes(ANY)
        mocker.result({'080112-05000': [23]})
        fake_xmlrpc_ticket.system_updateTicketStatusType('080112-05000', 1)
        mocker.result(1234)
        mocker.count(1,1)
        mocker.replay()

        #response = self.app.get(url_for(controller='periodic_update', action='update_tickets'))
        periodic_update.PeriodicUpdate.update_tickets()
        mocker.reset()
    
#     def testCloseServices(self):
#         self.mocker = Mocker()
#         fake_date = self.mocker.replace(datetime)
#         fake_date.now(ANY)
#         self.mocker.result(datetime(2008, 1, 10, 14))
#         self.mocker.count(0,5)
#         fake_xmlrpc_ticket = self.mocker.replace(core_xmlrpc.Ticket)
#         fake_xmlrpc_ticket.system_getTicketsStatusTypes(ANY)
#         self.mocker.result({'080112-05000': [19], '080112-00443':[19], '080112-00456':[23]})
#         self.mocker.replay()

#         #response = self.app.get(url_for(controller='periodic_update', action='close_services'))
#         periodic_update.PeriodicUpdate.close_services()
#         service = db_sess.query(ScheduledService).get(3)
#         #self.assertEqual(service.maintenance.state_id, 3)
#         self.mocker.restore()
    
    def test_stale_maintenance_cleanup(self):
        """Add a stale and a new maintenace, and test the stale maintenance cleanup
        functionality only cancels the old one."""
        db_sess.begin_nested()
        new_maint = ScheduledMaintenance()
        new_maint.creation_date = datetime.now()
        db_sess.save(new_maint)
        db_sess.begin_nested()
        old_maint = ScheduledMaintenance()
        old_maint.creation_date = datetime(2008, 1, 10, 14)
        db_sess.save(old_maint)
        stale_maints_just_closed = periodic_update.PeriodicUpdate.stale_maintenance_cleanup()
        self.assert_(old_maint.id in stale_maints_just_closed, "Old maintenance must be closed out.")
        self.assert_(new_maint.id not in stale_maints_just_closed, 
                "Newly created maintenance should not be closed for two hours after being created")

    def testPastDueServices(self):
        db_sess.begin_nested()
        old_serv = ScheduledService()
        old_serv.start_time = datetime(2008, 1, 10, 14)
        old_serv.state_id = ScheduledService.State.SCHEDULED
        db_sess.save(old_serv)

        expired_serv_ids = periodic_update.PeriodicUpdate.expire_past_due_services()
        self.assert_(old_serv.id in expired_serv_ids, "Old Service should be expired.")
        fresh_copy_of_old_serv = db_sess.query(ScheduledService).get(old_serv.id)
        self.assertEqual(fresh_copy_of_old_serv.state_id, ScheduledService.State.PAST_DUE)

