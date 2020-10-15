from maintcal.tests.lib import url_for, MaintcalFunctionalTest

import simplejson

from maintcal.model import db_sess, MaintenanceCategory

class TestMaintenancecategoriesController(MaintcalFunctionalTest):

    def test_new(self):
        response = self.app.get(url_for(controller='maintenancecategories', action='new'))
    
    def test_edit(self):
        response = self.app.get(url_for(controller='maintenancecategories', action='edit', id=1))
    
    def test_delete(self):
        response = self.app.post('/maintenancecategories/delete/1')
    
    def test_show(self):
        response = self.app.get(url_for(controller='maintenancecategories', action='show', id=1, format='html'))
    
    def test_index(self):
        response = self.app.get(url_for(controller='maintenancecategories'))
        # Test response...
    
    def test_index_json(self):
        response = self.app.get(url_for(controller='maintenancecategories', format='json'))
        self.assert_(response.body)
        mcs = simplejson.loads(response.body)
        self.assert_(len(mcs) >= 2)
    
    def test_show_json(self):
        response = self.app.get(url_for(controller='maintenancecategories', action='show', id=1, format='json'))
        self.assertEqual(response.status, 200)
        
        mc = simplejson.loads(response.body)
        self.assertEqual(mc['name'], 'Implementation Call')
        self.assertEqual(mc['description'], 'imp call desc')
    
    def test_show_bad_id(self):
        response = self.app.get(url_for(controller='maintenancecategories', action='show', id=2000), status=404)
        self.assertEqual(response.status, 404)
    
    def test_create(self):
        new_mc = {
            'name' : 'New Maintenance',
            'description' : 'description field'
        }
        
        response = self.app.post(url_for(controller='maintenancecategories', action='create'), params=new_mc)
        self.assert_(response.body)
        
        id = int(response.body)
        mc = db_sess.query(MaintenanceCategory).get(id)
        self.assertEqual(mc.name, 'New Maintenance')
        self.assertEqual(mc.description, 'description field')

    def test_create_empty_params(self):
        new_mc = {
            #'name' : 'New Maintenance',
            #'description' : 'description field'
        }
        
        response = self.app.post(url_for(controller='maintenancecategories', action='create'), params=new_mc)
        self.assert_(response.body)
        
        id = int(response.body)
        mc = db_sess.query(MaintenanceCategory).get(id)
        self.assertEqual(mc.name, None)
        self.assertEqual(mc.description, None)
    
    def test_update(self):
        new_mc = {
            'name' : 'Blah',
            'description' : 'blah desc'
        }
        
        response = self.app.post('/maintenancecategories/update/1', params=new_mc)
        self.assertEqual(response.status, 200)
        self.assert_(response.body)
        
        id = int(response.body)
        #id = 1
        mc = db_sess.query(MaintenanceCategory).get(id)
        self.assert_(mc, "Newly created maintenance category '%s' should exist" % id)
        self.assertEqual(mc.name, 'Blah')
        self.assertEqual(mc.description, 'blah desc')
    
    def test_update_empty_params(self):
        response = self.app.post('/maintenancecategories/update/1', params={})
        self.assertEqual(response.status, 200)
        self.assert_(response.body)
        
        id = int(response.body)
        mc = db_sess.query(MaintenanceCategory).get(id)
        self.assert_(mc, "Update maintenance category '%s' should exist" % id)
        self.assertEqual(mc.name, 'Implementation Call')
        self.assertEqual(mc.description, 'imp call desc')
    
    def test_update_blank_params(self):
        new_mc = {
            'name' : '',
            'description' : ''
        }
        
        response = self.app.post('/maintenancecategories/update/1', params=new_mc)
        self.assertEqual(response.status, 200)
        self.assert_(response.body)
        
        id = int(response.body)
        id=1
        mc = db_sess.query(MaintenanceCategory).get(id)
        self.assert_(mc, "Updated maintenance category '%s' should exist" % id)
        self.assertEqual(mc.name, '')
        self.assertEqual(mc.description, '')
    
    def test_update_bad_id(self):
        response = self.app.post('/maintenancecategories/update/2000', params={}, status=404)
        self.assertEqual(response.status, 404)
