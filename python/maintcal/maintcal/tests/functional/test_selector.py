from maintcal.tests.lib import url_for, MaintcalFunctionalTest
from maintcal.tests.data.data_helper import server_names_to_ids

from maintcal.lib import selector
from maintcal.model import db_sess, Server, ScheduledMaintenance

from datetime import datetime, timedelta

class TestSelector(MaintcalFunctionalTest):

    def local_setup(self):
        MaintcalFunctionalTest.local_setup(self)
        # Maintenances
        sm_move_server = ScheduledMaintenance('071215-00001')
        sm_move_server.service_type_id = 2
        sm_move_server.general_description = u'Move Server'
        sm_move_server.contact_id = 1
        sm_move_server.date_assigned = datetime(2008, 1, 1, 0, 0)
        sm_move_server.additional_duration = timedelta(minutes=60)
        sm_move_server.id = 220587
        #sm_move_server.servers = [server1]
        db_sess.save(sm_move_server)
        self.sm_move_server_id = sm_move_server.id

    def test_selector(self):
        self.dh.insertTestComputerByName('managed_linux_one')
        server_id = server_names_to_ids('managed_linux_one')[0]
        maint = db_sess.query(ScheduledMaintenance).get(self.sm_move_server_id)
        server = db_sess.query(Server).get(server_id)
        calendars = selector.select_calendars([server],
            maintenance_category_id=int(maint.maintenance_category),
            service_type_id=maint.service_type_id)

        # Assert the proper calendars and devices were chosen
        self.assertSelectCalendarsResults(calendars, 
            { 2: [server_id], 5: [server_id], 6: [server_id] })

    def assertSelectCalendarsResults(self, calendars, target_results):
        """
        calendars = results of calling select_calendars()

        target_results is of the form:

            dict( calendar_id => list of expected server ids for the given calendar id )

        example:

            { 1: [123123], 3: [123123, 222333] }
        """        
        # Verify the keys of calendars
        expected_calendar_ids = target_results.keys()
        received_calendar_ids = calendars.keys()
        self.assertEqual(set(expected_calendar_ids), set(received_calendar_ids))

        # Verify the contents of each calendar, both the length and the contents
        for calendar_id, server_list in calendars.items():
            server_id_set = set([s.id for s in server_list])
            self.assertEqual(server_id_set, set(target_results[calendar_id]))
                

    def test_selector_with_managed_storage(self):
        """Calling select_calendars() with a server with Managed Storage should return the Managed Storage Calendar"""
        maint = db_sess.query(ScheduledMaintenance).get(self.sm_move_server_id)
        server = db_sess.query(Server).get(176991)
        calendars = selector.select_calendars([server],
            maintenance_category_id=int(maint.maintenance_category),
            service_type_id=maint.service_type_id)
        self.assert_(4 in calendars.keys(), "Calendar 4 (Managed Storage) is not in list of required calendars")
        self.assert_(176991 in [s.id for s in calendars[4]], "Server 2 should be in Calendar 4 (Managed Storage)")
    
    def test_selector_with_two_servers(self):
        maint = db_sess.query(ScheduledMaintenance).get(self.sm_move_server_id)
        server1 = db_sess.query(Server).get(110912)
        server2 = db_sess.query(Server).get(110914)
        calendars = selector.select_calendars([server1, server2],
            maintenance_category_id=int(maint.maintenance_category),
            service_type_id=maint.service_type_id)
        self.assertEqual(set([3,5,6]), set(calendars.keys()))
        self.assert_(3 in calendars.keys(), "Calendar 3 (Intensive Windows) is not in list of required calendars")
        self.assert_(110912 in [s.id for s in calendars[3]], "Server 1 should be associated with calendar 3 (Intensive Windows)")
        self.assert_(110914 in [s.id for s in calendars[6]], "Server 3 should be associated with calendar 6 (Intensive Windows)")
