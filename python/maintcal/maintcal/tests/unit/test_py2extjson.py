from maintcal.tests.lib import MaintcalUnitTest
from maintcal.lib import py2extjson
import simplejson

class MyClass(object):
    def toDict(self):
        return {
            'name': 'class name',
            'description': 'class description'
        }

class TestPy2ExtJson(MaintcalUnitTest):
    
    def local_setup(self):
        self.myobj = MyClass()
    
    def test_dumps(self):
        """Test 'dumps' with full set of data"""
        result = py2extjson.py2extjson.dumps([self.myobj.toDict()])
        result_dict = simplejson.loads(result)
        
        self.assertEqual(result_dict['rows'][0], {'name': 'class name', 'description':'class description'})
    
    def test_dumps_list_coercion(self):
        """Test 'dumps' with full set of data. Single dict should be cast into a list."""
        result = py2extjson.py2extjson.dumps(self.myobj.toDict())
        result_dict = simplejson.loads(result)
        
        self.assertEqual(result_dict['rows'][0], {'name': 'class name', 'description':'class description'})
    
    def test_dumps_error(self):
        """'dumps' should raise TypeError when not passing a dict or list"""
        self.assertRaises(TypeError, py2extjson.py2extjson.dumps, self.myobj)
        self.assertRaises(TypeError, py2extjson.py2extjson.dumps, None)
        self.assertRaises(TypeError, py2extjson.py2extjson.dumps, 12)
    
    def test_dumps_empty_list(self):
        """Passing 'dumps' with an empty list should return metadata with empty values"""
        result = py2extjson.py2extjson.dumps([])
        result_dict = simplejson.loads(result)
        self.assertEqual(result_dict['rows'], [])
