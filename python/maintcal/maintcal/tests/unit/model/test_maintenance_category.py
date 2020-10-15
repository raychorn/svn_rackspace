from maintcal.tests.lib.unit import MaintcalUnitTest

from maintcal.model import db_sess, MaintenanceCategory

class TestMaintenanceCategory(MaintcalUnitTest):
    def local_setup(self):
        self.mcat = MaintenanceCategory('My Maint. Category', 'Description for my maintenance category')
        self.mcat.id = 1
        
    def local_teardown(self):
        pass
 
    def test_creation(self):
        self.assertEqual(self.mcat.description, 'Description for my maintenance category')
    
    def test_str_representation(self):
        self.assertEqual(self.mcat.__str__(), 'My Maint. Category')
        self.assertEqual(str(self.mcat), 'My Maint. Category')
        self.assertEqual("%s" % self.mcat, 'My Maint. Category')

    def test_int_representation(self):
        self.assertEqual(self.mcat.__int__(), 1)
        self.assertEqual(int(self.mcat), 1)
        self.assertEqual("%d" % self.mcat, '1')
