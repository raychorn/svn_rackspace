from maintcal.lib import json_tz
from maintcal.tests.lib import MaintcalUnitTest

class TestJsonTZ(MaintcalUnitTest):
    def local_setup(self):
        self.tzd = json_tz.JsonTz()
    
    def local_teardown(self):
        if json_tz.os.path.exists('/tmp/zonenames.js'):
            json_tz.os.unlink('/tmp/zonenames.js')
    
    def test_load_with_file(self):
        self.assertEqual(type(json_tz.file_util.load_zonetab_file(json_tz.ZONETAB_FILE)), type(''))
    
    def test_load_without_file(self):
        self.assertEqual(json_tz.file_util.load_zonetab_file('/bogus/file/name'), None)

    def test_parse_file(self):
        self.tzd.parse_file()
        self.assert_(self.tzd.tzdict.has_key('America'))
        self.assert_('Chicago' in self.tzd.tzdict['America'])
    
    def test_good_export(self):
        self.tzd.parse_file()
        self.tzd.export('/tmp')
        self.assert_(json_tz.os.path.exists('/tmp/zonenames.js'))
    
    def test_bad_export(self):
        self.tzd.parse_file()
        self.tzd.export('/tmp')
        json_tz.os.chmod('/tmp/zonenames.js', 0)
        self.assertRaises(IOError, self.tzd.export, '/tmp')
