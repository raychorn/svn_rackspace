from maintcal.tests.lib.unit import MaintcalUnitTest

from maintcal.model import db_sess, ScheduledService, Server

class TestScheduledService(MaintcalUnitTest):
    # These tests are probably unnecessary
    def local_setup(self):
        #init_db()
        #self.cal = Calendar('test cal', 'cal desc')
        #self.maint_obj = ScheduledMaintenance('071215-00005')
        #self.maint_obj.service_type = ServiceType('service type 1')
        #self.maint_obj.service_type.maintenance_category = MaintenanceCategory('maint cat 1')
        self.service = ScheduledService('sched. service')
    
    def test_server_list(self):
        self.service.servers = [Server(1), Server(2)]
