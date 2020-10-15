from maintcal.tests.lib import url_for, MaintcalFunctionalTest

import simplejson
from datetime import timedelta

from maintcal.model import db_sess, ServiceType

class TestServicetypesController(MaintcalFunctionalTest):

    def test_new(self):
        response = self.app.get(url_for(controller='servicetypes', action='new'))
    
    def test_edit(self):
        response = self.app.get(url_for(controller='servicetypes', action='edit', id=1))
    
    def test_delete(self):
        response = self.app.post('/servicetypes/delete/1')
    
    def test_show(self):
        response = self.app.get(url_for(controller='servicetypes', action='show', id=1, format='html'))
    
    def test_index(self):
        response = self.app.get(url_for(controller='servicetypes'))
        # Test response...

    def test_index_json(self):
        response = self.app.get(url_for(controller='servicetypes', format='json'))
        self.assertEqual(response.status, 200)
        
        stypes = simplejson.loads(response.body)
        self.assert_(len(stypes) >= 2)
    
    def test_index_active_json(self):
        response = self.app.get('/servicetypes/1.json')
        self.assertEqual(response.status, 200)
        all_stypes = simplejson.loads(response.body)
        
        url = '/servicetypes.json?id=1' 

        active_response = self.app.get(url, params={'active':True})
        self.assertEqual(active_response.status, 200)
        active_stypes = simplejson.loads(active_response.body)
        
        self.assert_(len(all_stypes) >= len(active_stypes), "%d is not greater than %d" % (len(all_stypes), len(active_stypes)))
    
    def test_index_admin_json(self):
        response = self.app.get(
            url_for(controller='servicetypes', format='json'),
            params = {'admin' : True})
        self.assertEqual(response.status, 200)
        all_stypes = simplejson.loads(response.body)
        for stype in all_stypes['rows']:
            mod_c = stype.get('modification_contact')
            if stype.get('id') in [1,2]:
                self.assertEqual(mod_c,u'nath6666')
            else:
                self.assertEqual(mod_c,u'')
            

    def test_show_json(self):
        # stype is an EXTJS specific json object. 
        response = self.app.get(url_for(controller='servicetypes', action='show', id=1, format='json'))
        self.assertEqual(response.status, 200)
        
        stype = simplejson.loads(response.body)
        self.assertEqual(stype['rows'][0]['name'], 'Implementation Call')
        self.assertEqual(stype['rows'][0]['description'], 'imp call desc')
        self.assertEqual(stype['rows'][0]['active'], True)
        self.assertEqual(stype['rows'][0]['length_seconds'], 14400)
        self.assertEqual(stype['rows'][0]['length_hours'], 4)
        self.assertEqual(stype['rows'][0]['lead_time_seconds'], 14400)
        self.assertEqual(stype['rows'][0]['lead_time_hours'], 4)
        self.assertEqual(stype['rows'][0]['maintenance_category_id'], 1)
        self.assertEqual(stype['rows'][0]['maintenance_category'], 'Implementation Call')
    
    def test_show_bad_id(self):
        response = self.app.get(url_for(controller='servicetypes', action='show', id=2000, format='json'), status=404)
        self.assertEqual(response.status, 404)
    
    def test_create(self):
        new_st = {
            'name' : 'Test service',
            'description' : 'A test service type',
            'active' : True,
            'length_hours' : 1,
            'lead_time_hours' : 4,
            'maintenance_category_id' : 1,
        }
        
        response = self.app.post(url_for(controller='servicetypes', action='create'), params=new_st)
        self.assertEqual(response.status, 200)
        self.assert_(response.body)
        
        st_id = int(response.body)
        st = db_sess.query(ServiceType).get(st_id)
        
        self.assertEqual(st.name, 'Test service')
        self.assertEqual(st.description, 'A test service type')
        self.assertEqual(st.active, True)
        self.assertEqual(st.length, timedelta(hours=1))
        self.assertEqual(st.lead_time, timedelta(hours=4))
        self.assertEqual(st.maintenance_category.id, 1)
    
    def test_create_empty_maint_cat(self):
        new_st = {
            #'name' : 'Test service',
            #'description' : 'A test service type',
            #'active' : True,
            #'length_seconds' : 3600,
            #'lead_time_seconds' : 14400,
            #'maintenance_category_id' : 1,
        }        
        response = self.app.post(url_for(controller='servicetypes', action='create'), params=new_st, status=400)
        self.assertEqual(response.status, 400)
    
    def test_create_empty_timedeltas_equal_zero(self):
        new_st = {
            'name' : 'Test service',
            'description' : 'A test service type',
            'active' : True,
            #'length_seconds' : 3600,
            #'lead_time_seconds' : 14400,
            'maintenance_category_id' : 1,
        }        
        response = self.app.post(url_for(controller='servicetypes', action='create'), params=new_st)
        self.assertEqual(response.status, 200)
        
        st = db_sess.query(ServiceType).get(int(response.body))
        self.assertEqual(st.length, timedelta(0))
        self.assertEqual(st.lead_time, timedelta(0))

    def test_create_empty_name_description_active(self):
        new_st = {
            #'name' : 'Test service',
            #'description' : 'A test service type',
            #'active' : True,
            'length_hours' : 1,
            'lead_time_hours' : 4,
            'maintenance_category_id' : 1,
        }        
        response = self.app.post(url_for(controller='servicetypes', action='create'), params=new_st, status=400)
        self.assertEqual(response.status, 400)
    
    def test_update(self):
        new_st = {
            'name' : 'Updated name',
            'description' : 'updated description',
            'active' : False,
            'length_hours' : 2,
            'lead_time_hours' : 10,
            'maintenance_category_id' : 2
        }
        
        response = self.app.post('/servicetypes/update/1', params=new_st)
        self.assertEqual(response.status, 200)
        self.assertEqual(int(response.body), 1)
        
        st = db_sess.query(ServiceType).get(int(response.body))
        
        self.assertEqual(st.name, 'Updated name')
        self.assertEqual(st.description, 'updated description')
        self.assertEqual(st.active, False)
        self.assertEqual(st.length, timedelta(hours=2))
        self.assertEqual(st.lead_time, timedelta(hours=10))
        self.assertEqual(st.maintenance_category.id, 2)
    
    def test_update_empty_data(self):
        new_st = {
        }
        
        response = self.app.post('/servicetypes/update/1', params=new_st)
        self.assertEqual(response.status, 200)
        self.assertEqual(int(response.body), 1)
        
        st = db_sess.query(ServiceType).get(int(response.body))
        
        self.assertEqual(st.name, 'Implementation Call')
        self.assertEqual(st.description, 'imp call desc')
        self.assertEqual(st.active, True)
        self.assertEqual(st.length, timedelta(seconds=14400))
        self.assertEqual(st.lead_time, timedelta(seconds=14400))
        self.assertEqual(st.maintenance_category.id, 1)
    
    def test_update_bad_id(self):
        response = self.app.post('/servicetypes/update/2000', status=404, params={})
        self.assertEqual(response.status, 404)
    
    def test_update_blank_data(self):
        new_st = {
            'name' : '',
            'description' : '',
            'active' : '',
            'length_hours' : 0,
            'lead_time_hours' : 0,
            'maintenance_category_id' : 1
        }
        
        response = self.app.post('/servicetypes/update/1', params=new_st)
        self.assertEqual(response.status, 200)
        self.assertEqual(int(response.body), 1)
        
        st = db_sess.query(ServiceType).get(int(response.body))
        
        self.assertEqual(st.name, '')
        self.assertEqual(st.description, '')
        self.assertEqual(st.active, False)
        self.assertEqual(st.length, timedelta(hours=0))
        self.assertEqual(st.lead_time, timedelta(hours=0))
        self.assertEqual(st.maintenance_category.id, 1)
    
    def test_update_bad_time_length_hours(self):
        response = self.app.post('/servicetypes/update/1', params={'length_hours': 'hello'}, status=400)
        self.assertEqual(response.status, 400)
    
    def test_update_bad_lead_time_hours(self):
        response = self.app.post('/servicetypes/update/1', params={'lead_time_hours': 'hello'}, status=400)
        self.assertEqual(response.status, 400)
    
    def test_update_bad_category_ids(self):
        response = self.app.post('/servicetypes/update/1', params={'maintenance_category_id': 'hello'}, status=400)
        self.assertEqual(response.status, 400)
    
