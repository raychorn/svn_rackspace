from maintcal.tests.lib.unit import MaintcalUnitTest

from maintcal.model import db_sess, Contact

class TestContact(MaintcalUnitTest):
    def local_setup(self):
        self.contact = Contact(61887)
        #self.contact_id = 61887
        self.contact.first_name = "Jim"
        self.contact.last_name = "Bob"
        self.contact.username = 'jim.bob'
        
    def test_str_representation(self):
        self.assertEqual(str(self.contact), "jim.bob")
        self.assertEqual(self.contact.__str__(), "jim.bob")
        self.assertEqual("%s" % self.contact, "jim.bob")
    
    def test_int_representation(self):
        self.assertEqual(int(self.contact), 61887)
        self.assertEqual(self.contact.__int__(), 61887)
        self.assertEqual("%d" % self.contact, '61887')
