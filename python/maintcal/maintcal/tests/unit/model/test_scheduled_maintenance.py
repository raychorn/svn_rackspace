from maintcal.tests.lib import MaintcalUnitTest

from maintcal.model import db_sess, ScheduledMaintenance, ServiceType, MaintenanceCategory
from maintcal.model import ScheduledService, Calendar, Server

class TestScheduledMaintenance(MaintcalUnitTest):
    def local_setup(self):
        self.maint_obj = ScheduledMaintenance('071215-00005')
        self.maint_obj.service_type = ServiceType('service type 1')
        self.maint_obj.service_type.maintenance_category = MaintenanceCategory('maint cat 1')
        self.cal = Calendar('test cal', 'cal desc')
        self.service_obj = ScheduledService('sched. service')
        self.service_obj.maintenance = self.maint_obj
        
    def test_creation_ticket_number_saved(self):
        self.assertEqual(self.maint_obj.master_ticket, '071215-00005')
        
    def test_creation_assert_state_object_created(self):
        self.assertEqual(self.maint_obj.state_id, 1)
        self.assertEqual(self.maint_obj.state.name, 'Temporary')
    
    def test_state_created(self):
        self.assert_(self.maint_obj.state)
    
    def test_state_cached(self):
        state_1st_get = self.maint_obj.state
        state_2nd_get = self.maint_obj.state
        self.assert_(state_1st_get is state_2nd_get)
    
    def test_maintenance_category_attr(self):
        self.assertEqual(self.maint_obj.maintenance_category.name, 'maint cat 1')
    
    def test_get_servers(self):
        self.service_obj.servers = [Server(1), Server(2)]
        self.assert_(self.maint_obj.servers)
