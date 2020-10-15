from maintcal.tests.lib import url_for, MaintcalFunctionalTest

import simplejson
from datetime import datetime, timedelta

from maintcal.lib import core_xmlrpc
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from maintcal.model import db_sess
from maintcal.model import MaintenanceCategory, ServiceType, ScheduledMaintenance, ScheduledService

class TestMaintenancesController(MaintcalFunctionalTest):

    def test_new(self):
        response = self.app.get(url_for(controller='maintenances', action='new'))
    
    def test_edit(self):
        response = self.app.get(url_for(controller='maintenances', action='edit', id=1))
        response = self.app.get(url_for(controller='maintenances', action='edit', id=2000), status=404)


    def test_delete(self):
        response = self.app.post('/maintenances/delete/1')


    def test_show(self):
        response = self.app.get(url_for(controller='maintenances', action='show', id=1, format='html', tzname='UTC'))


    def test_index(self):
        response = self.app.get(url_for(controller='/maintenances'))
        # Test response...


    def test_create(self):
        self.mockAuthToken()
        self.mockServerGetDetailsByComputers()
        self.mockTicketGetTicket()
        maint_params = {
                'master_ticket' : '080102-00121',
                'description' : 'do stuff',
                'expedite' : False,
                #'billing_text' : 'send me the bill',
                'additional_duration_minutes': '60',
                'service_type_id' : 1,
                #'employee_contact_id' : 1,
                'contact_name' : 'bob.racker',
                'servers' : 110912
        }
        response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params)
        self.assertEqual(response.status, 200)
        self.assert_(response.body)
        
        new_maint = db_sess.query(ScheduledMaintenance).filter_by(master_ticket='080102-00121').one()
        self.assert_(new_maint)
        self.assertEqual(new_maint.general_description, 'do stuff')
        self.assertEqual(new_maint.expedite, False)
        self.assertEqual(new_maint.additional_duration, timedelta(minutes=60))
        self.assertEqual(new_maint.service_type_id, 1)
        self.assertEqual(str(new_maint.service_type), 'Implementation Call')
        #self.assertEqual(new_maint.contact_id, 1)
        self.assertEqual(new_maint.state_id, 1)


    def test_create_with_multiple_servers(self):
        self.mockAuthToken()
        self.mockServerGetDetailsByComputers()
        self.mockTicketGetTicket()
        maint_params = "master_ticket=080102-00121&service_type_id=1&employee_contact_id=1&servers=110912&servers=110945"
        response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params)
        self.assertEqual(response.status, 200)
        self.assert_(response.body)
        
        new_maint = db_sess.query(ScheduledMaintenance).filter_by(master_ticket='080102-00121').one()
        self.assert_(new_maint)
        self.assert_(110912 in [s.id for s in new_maint.servers])
        self.assert_(110945 in [s.id for s in new_maint.servers])
        self.assert_(new_maint.services, "Maintenance must have services associated with it")


    def test_create_with_bad_server(self):
        """Creating a maintenance with a bad server number should return a 400"""
        self.mockAuthToken()
        self.mockServerGetDetailsByComputers()
        self.mockTicketGetTicket()
        maint_params = "master_ticket=080102-00121&service_type_id=1&employee_contact_id=1&servers=9999"
        response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params, status=400)
        self.assertEqual(response.status, 400)


    # not getting this in request.params anymore.
    #def test_create_missing_employee(self):
    #    """Status code should be 400 when missing employee number."""
    #    maint_params = {
    #        'master_ticket' : '080102-00121',
    #        'description' : 'do stuff',
    #        'expedite_text' : 'do it faster',
    #        'billing_text' : 'send me the bill',
    #        'additional_duration_minutes': '60',
    #        'service_type_id' : 1,
    #        #'employee_contact_id' : 1
    #    }
    #    response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params, status=400)
    #    self.assertEqual(response.status, 400)


    def test_create_missing_server_list(self):
        """Status code should be 400 when missing server_list."""
        self.mockTicketGetTicket()
        maint_params = {
                'master_ticket' : '080102-00121',
                'description' : 'do stuff',
                'expedite' : False,
                'additional_duration_minutes': '60',
                'service_type_id' : 1,
                'employee_contact_id' : 1
        }
        response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params, status=400)
        self.assertEqual(response.status, 400)


    def test_create_missing_service_type(self):
        """Status code should be 400 when missing employee number."""
        self.mockTicketGetTicket()
        maint_params = {
                'master_ticket' : '080102-00121',
                'description' : 'do stuff',
                'expedite' : False,
                #'billing_text' : 'send me the bill',
                'additional_duration_minutes': '60',
                #'service_type_id' : 1,
                'employee_contact_id' : 1
        }
        response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params, status=400)
        self.assertEqual(response.status, 400)


    def test_create_missing_additional_duration(self):
        """Should be able to create an object without additional duration."""
        self.mockAuthToken()
        self.mockServerGetDetailsByComputers()
        self.mockTicketGetTicket()
        maint_params = {
                'master_ticket' : '080102-00121',
                'description' : 'do stuff',
                'expedite' : False,
                'billing_text' : 'send me the bill',
                #'additional_duration_minutes': '60',
                'service_type_id' : 1,
                'employee_contact_id' : 1,
                'servers' : 110912
        }
        response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params)
        self.assertEqual(response.status, 200)
        new_maint = db_sess.query(ScheduledMaintenance).filter_by(master_ticket='080102-00121').one()
        self.assertEqual(new_maint.additional_duration, timedelta(minutes=0))


    def test_create_missing_ticket(self):
        """Should not be able to create an object without ticket."""
        maint_params = {
                #'master_ticket' : '080102-00121',
                'description' : 'do stuff',
                'expedite_text' : 'do it faster',
                'billing_text' : 'send me the bill',
                #'additional_duration_minutes': '60',
                'service_type_id' : 1,
                'employee_contact_id' : 1
        }
        response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params, status=400)
        self.assertEqual(response.status, 400)


    def test_create_bad_service_type(self):
        """Should not be able to create an object without a valid service type."""
        self.mockTicketGetTicket()
        maint_params = {
                'master_ticket' : '080102-00121',
                'description' : 'do stuff',
                'expedite_text' : 'do it faster',
                'billing_text' : 'send me the bill',
                #'additional_duration_minutes': '60',
                'service_type_id' : 'hello',
                'employee_contact_id' : 1
        }
        response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params, status=400)
        self.assertEqual(response.status, 400)


    #def test_create_bad_employee_contact(self):
    #    """Should not be able to create an object without a valid employee contact."""
    #    maint_params = {
    #        'master_ticket' : '080102-00121',
    #        'description' : 'do stuff',
    #        'expedite_text' : 'do it faster',
    #        'billing_text' : 'send me the bill',
    #        #'additional_duration_minutes': '60',
    #        'service_type_id' : 1,
    #        'employee_contact_id' : 'mikey roberts'
    #    }
    #    response = self.app.post(url_for(controller='/maintenances', action='create'), params=maint_params, status=400)
    #    self.assertEqual(response.status, 400)


    def test_show_json(self):
        response = self.app.get(url_for(controller='/maintenances', action='show', id='1', format='json', tzname='UTC'))
        #mig_server_maint_db = session.query(ScheduledMaintenance).filter_by(id=1)[0]
        self.assertEqual(response.status, 200)
        #print response.body
        app_body = response.body
        mig_sm = simplejson.loads(app_body)
        self.assertEqual(mig_sm["general_description"], "Move Server")
        self.assertEqual(mig_sm["service_type"], "Cabinet Migration")
        self.assertEqual(mig_sm["service_type_id"], 2)
        self.assertEqual(mig_sm["master_ticket"], "071215-00001")
        self.assertEqual(mig_sm["state"], "Temporary")
        self.assertEqual(mig_sm["state_id"], 1)
        self.assertEqual(mig_sm["expedite"], False)
        self.assertEqual(mig_sm["contact"], "john.doe")
        self.assertEqual(mig_sm["contact_id"], 1)
        #self.assertEqual(mig_sm["contact_first_name"], "John")
        #self.assertEqual(mig_sm["contact_last_name"], "Doe")
        self.assertEqual(mig_sm["maintenance_category_id"], 2)
        self.assertEqual(mig_sm["maintenance_category"], 'Server Migration')
        self.assertEqual(mig_sm["additional_duration"], str(timedelta(minutes=60)))
        self.assert_(110912 in [s[0] for s in mig_sm["servers"]], "Server 1 is not in %s" % mig_sm["servers"])
        self.assert_(110945 in [s[0] for s in mig_sm["servers"]], "Server 3 is not in %s" % mig_sm["servers"])


# Commmented out because it doesn't work right. We're switching to UTC and this has bad expectations.
# the expectations for the start_time are 6 hours off since we have switched the test db to postgres
# It is not currently worth the time to try and figure out the correct expectations to use.
#    def test_show_sjson(self):
#        response = self.app.get(url_for(controller='/maintenances', action='show', id='1', format='sjson'))
#        self.assertEqual(response.status, 200)
#        app_body = response.body
#        res = simplejson.loads(app_body)
#        self.assertEqual(res["general_description"], "Move Server")
#        self.assertEqual(res["service_type"], "Cabinet Migration")
#        self.assertEqual(res["service_type_id"], 2)
#        self.assertEqual(res["master_ticket"], "071215-00001")
#        self.assertEqual(res["start_time"], 1199988000)
#        self.assertEqual(res["end_time"], 1199995200) 
#        self.assertEqual(res["status"], "Temporary")
#        self.assertEqual(res["expedite"], False)
#        self.assertEqual(res["contact"], "john.doe")
#        self.assertEqual(res["date_assigned"],1199167200)
#        self.assertEqual(res["maintenance_category"], 'Server Migration')
#        self.assertEqual(res["additional_duration"],60)
#        # These asserts are pretty lame, but for lack of time, info will have to do.
#        self.assertEqual(len(res["devices"]),2)
#        self.assertEqual(len(res["services"]),2)


    def test_show_json_empty_data(self):
        response = self.app.get(url_for(controller='maintenances', action='show', id='2', format='json', tzname='UTC'))
        #mig_server_maint_db = session.query(ScheduledMaintenance).filter_by(id=1)[0]
        self.assertEqual(response.status, 200)
        app_body = response.body
        mig_sm = simplejson.loads(app_body)
        self.assertEqual(mig_sm["general_description"], "")
        self.assertEqual(mig_sm["service_type"], "")
        self.assertEqual(mig_sm["service_type_id"], None)
        self.assertEqual(mig_sm["master_ticket"], "")
        self.assertEqual(mig_sm["state"], "Temporary")
        self.assertEqual(mig_sm["state_id"], 1)
        self.assertEqual(mig_sm["contact"], "")
        self.assertEqual(mig_sm["contact_id"], None)
        #self.assertEqual(mig_sm["contact_first_name"], "John")
        #self.assertEqual(mig_sm["contact_last_name"], "Doe")
        self.assertEqual(mig_sm["maintenance_category_id"], None)
        self.assertEqual(mig_sm["maintenance_category"], '')
        self.assertEqual(mig_sm["additional_duration"], str(timedelta(0)))
        self.assertEqual(mig_sm["servers"], [])


    def test_show_sjson_empty_data(self):
        response = self.app.get(url_for(controller='/maintenances', action='show', id='2', format='json', tzname='UTC'))
        self.assertEqual(response.status, 200)
        app_body = response.body
        res = simplejson.loads(app_body)
        self.assertEqual(res["general_description"], "")
        self.assertEqual(res["service_type"], "")
        self.assertEqual(res["service_type_id"], None)
        self.assertEqual(res["master_ticket"], "")
        #self.assertEqual(res["start_time"], "")
        #self.assertEqual(res["end_time"], "") 
        #self.assertEqual(res["status"], "Temporary")
        self.assertEqual(res["expedite"], False)
        self.assertEqual(res["contact"], "")
        #self.assertEqual(res["date_assigned"],"")
        self.assertEqual(res["maintenance_category"], '')
        self.assertEqual(res["additional_duration"], str(timedelta(0)))
        # These asserts are pretty lame, but for lack of time, info will have to do.
        #self.assertEqual(len(res["devices"]),0)
        #self.assertEqual(len(res["services"]),0)

    
    def test_show_bad_id(self):
        response = self.app.get(url_for(controller='/maintenances', action='show', id='22'), status=404)
        self.assertEqual(response.status, 404)


    def test_update_all_values(self):
        maint_params = {
                #'id': 1,
                #'_method' : 'PUT',
                'master_ticket' : '080102-00121',
                'description' : 'do stuff',
                'expedite' : True,
                #'billing_text' : 'send me the bill',
                'additional_duration_minutes': '120',
                'service_type_id' : 1,
                'employee_contact_id' : 1
        }
        response = self.app.post('/maintenances/update/1', params=maint_params)
        self.assertEqual(response.status, 200)
        
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        self.assert_(new_maint)
        self.assertEqual(new_maint.master_ticket, '080102-00121')
        self.assertEqual(new_maint.general_description, 'do stuff')
        self.assertEqual(new_maint.expedite, True)
        #self.assertEqual(new_maint.billing_text, 'send me the bill')
        self.assertEqual(new_maint.additional_duration, timedelta(minutes=120))
        self.assertEqual(new_maint.service_type_id, 1)
        self.assertEqual(str(new_maint.service_type), 'Implementation Call')
        self.assertEqual(new_maint.contact_id, 1)
        self.assertEqual(new_maint.state_id, 1)


    def test_update_bad_id(self):
        response = self.app.post('/maintenances/update/12', status=404)
        self.assertEqual(response.status, 404)


    def test_update_missing_params(self):
        """Missing parameters should be ignored. Original values should be maintained. Text parameters must be left untouched."""
        maint_params = {
                #'id': 1,
                #'_method' : 'PUT',
                #'master_ticket' : '080102-00121',
                #'description' : 'do stuff',
                #'expedite_text' : 'do it faster',
                #'billing_text' : 'send me the bill',
                #'additional_duration_minutes': '60',
                #'service_type_id' : 1,
                #'employee_contact_id' : 1
        }
        response = self.app.post('/maintenances/update/1', params=maint_params)
        self.assertEqual(response.status, 200)
        
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        self.assert_(new_maint)
        self.assertEqual(new_maint.master_ticket, '071215-00001')
        self.assertEqual(new_maint.general_description, 'Move Server')
        self.assertEqual(new_maint.expedite, False)
        self.assertEqual(new_maint.additional_duration, timedelta(minutes=60))
        self.assertEqual(new_maint.service_type_id, 2)
        self.assertEqual(str(new_maint.service_type), 'Cabinet Migration')
        self.assertEqual(new_maint.contact_id, 1)
        self.assertEqual(new_maint.state_id, 1)


    def test_update_empty_string(self):
        """Text explicitly set to empty strings should be saved as empty strings."""
        maint_params = {
                #'id': 1,
                #'_method' : 'PUT',
                'master_ticket' : '',
                'description' : '',
                'expedite' : '',
                #'billing_text' : '',
                'additional_duration_minutes': '60',
                'service_type_id' : 1,
                'employee_contact_id' : 1
        }
        response = self.app.post('/maintenances/update/1', params=maint_params)
        self.assertEqual(response.status, 200)
        
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        self.assert_(new_maint)
        self.assertEqual(new_maint.master_ticket, '')
        self.assertEqual(new_maint.general_description, '')
        self.assertEqual(new_maint.expedite, False)
        self.assertEqual(new_maint.additional_duration, timedelta(minutes=60))
        self.assertEqual(new_maint.service_type_id, 1)
        self.assertEqual(str(new_maint.service_type), 'Implementation Call')
        self.assertEqual(new_maint.contact_id, 1)
        self.assertEqual(new_maint.state_id, 1)


    def test_update_bad_service_type(self):
        response = self.app.post('/maintenances/update/1', params={'service_type_id': 'aeu'}, status = 400)
        self.assertEqual(response.status, 400)


#     def test_update_bad_employee_name(self):
#         response = self.app.post('/maintenances/update/2', params={'employee_contact_id': 'aoeu'}, status = 400)
#         self.assertEqual(response.status, 400)


    def test_update_bad_additional_minutes(self):
        response = self.app.post('/maintenances/update/1', params={'additional_duration_minutes': 'aoeu'}, status = 400)
        self.assertEqual(response.status, 400)


    def test_update_server_list_shrink_server_count(self):
        self.mockAuthToken()
        self.mockServerGetDetailsByComputers()
        response = self.app.post('/maintenances/update/1', params="servers=110945")
        
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        self.assertEqual([s.id for s in new_maint.servers], [110945] )


    # TODO: verify test logic and purpose
    #def test_update_server_list_delete_services(self):
    #    response = self.app.post('/maintenances/update/1', params="servers=110912")
    #    
    #    new_maint = db_sess.query(ScheduledMaintenance).get(1)
    #    self.assertEqual([s.id for s in new_maint.servers], [110912] )


    def test_update_server_list_add_services(self):
        self.mockAuthToken()
        self.mockServerGetDetailsByComputers()
        response = self.app.post('/maintenances/update/1', params="servers=110912&servers=110914&servers=110945")
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        self.assertEqual(set([110912,110914,110945]), set([s.id for s in new_maint.servers]))


    def test_update_service_type(self):
        self.broken_test()
        return
        # TODO: AUDIT LATER WITH NATHEN
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        print "no of services: ", len(new_maint.services)
        response = self.app.post('/maintenances/update/1', params={'service_type_id': 1})
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        self.assert_(110912 in [s.id for s in new_maint.servers])
        self.assert_(110945 in [s.id for s in new_maint.servers])
        self.assertEqual(len(new_maint.services), 2)
        self.assertEqual(new_maint.services[0].calendar.name, 'Managed Linux')
        self.assertEqual(new_maint.services[1].calendar.name, 'Intensive Windows')


    def test_update_service_type_and_servers(self):
        self.broken_test()
        return
        response = self.app.post('/maintenances/update/1', params="servers=110912&service_type_id=1")
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        self.assert_(110912 in [s.id for s in new_maint.servers])
        #print new_maint.services
        self.assertEqual(len(new_maint.services), 1)
        #self.assertEqual(new_maint.services[0].calendar.name, 'Intensive Windows')


    def test_confirm_maintenance(self):
        self.mockTicketCreateSubTicket()
        response = self.app.post(url_for(controller='maintenances', action='confirm', id=4))
        #print "body: " ,response.body
        new_maint = db_sess.query(ScheduledMaintenance).get(4)
        self.assertEqual(new_maint.state_id, 3)


    def test_confirm_maintenance_fail(self):
        response = self.app.post(url_for(controller='maintenances', action='confirm', id=1), status=400)


    def test_ticket_single_good(self):
        response = self.app.get(url_for(
                controller='maintenances', action='ticket', id='071215-00001'))
        self.assertEqual(simplejson.loads(response.body),[1])


    def test_ticket_multiple_good(self):
        response = self.app.get(url_for(
                controller='maintenances', action='ticket', id='080101-00002'))
        self.assertEqual(set(simplejson.loads(response.body)),set([3,4,5]))


    def test_ticket_bad_in(self):
        response = self.app.get(url_for(
                controller='maintenances', action='ticket', id='jklsfdjklsfd'),status=404)


    def test_ticket_no_maint(self):
        response = self.app.get(url_for(
                controller='maintenances', action='ticket', id='071215-00002'),status=404)


    def test_cancel_maintenance(self):
        response = self.app.post(url_for(controller='maintenances', action='cancel', id=4))
        new_maint = db_sess.query(ScheduledMaintenance).get(4)
        self.assertEqual(new_maint.state_id, 4)


    def test_cancel_maintenance_with_cancel_message(self):
        response = self.app.post(url_for(controller='maintenances', action='cancel', id=4),
                params={'cancel_message':'canceled!'})
        new_maint = db_sess.query(ScheduledMaintenance).get(4)
        self.assertEqual(new_maint.state_id, 4)


    def test_cancel_maintenance_with_services_and_tickets(self):
        self.mockAuthToken()
        self.mockServerGetDetailsByComputers()
        self.mockTicketGetTicket()
        self.mockTicketAddMessage()
        self.mockTicketSystemUpdateTicketStatusType()
        response = self.app.post(url_for(controller='maintenances', action='cancel', id=1),
                params = {'cancel_message':'canceled!'})
        new_maint = db_sess.query(ScheduledMaintenance).get(1)
        self.assertEqual(new_maint.state_id, 4)


    def _getNowAsDict(self, add_hours=None):
        safetznow = self.safetznow()

        if add_hours:
            safetznow = safetznow + timedelta(hours=add_hours)

        result = {}
        result['start_year'] = safetznow.year
        result['start_month'] = safetznow.month
        result['start_day'] = safetznow.day
        result['start_hour'] = safetznow.hour
        result['start_minute'] = safetznow.minute

        return result

    def test_schedule(self):
        self.mockTicketAddMessage()
        # start five hours from now
        params = self._getNowAsDict(add_hours=5)
        params['tzname'] = 'UTC'
        params['is_dst'] = '0'
        response = self.app.post(url_for(controller='maintenances', action='schedule', id=3),
                params=params)
               
        self.assert_(response.body)

    def test_schedule_across_dst(self):
        """ This test will not be valid when run on the same side of a dst break.
            E.G. both the requested time and the time when the test is run have the same dst flag.
        """
        self.mockTicketAddMessage()
        # start five hours from now
        params = self._getNowAsDict(add_hours=266) # 11 days 2 hours from now
        target = self._getNowAsDict(add_hours=271) # this implies a maintenance scheduled at CST(-6 UTC) into CDT (-5 CDT) 
        target_maintcal_datetime = MaintcalDatetime(
            int(target['start_year']),
            int(target['start_month']),
            int(target['start_day']),
            int(target['start_hour']), 
            int(params['start_minute']),0) 
        params['tzname'] = 'America%2FChicago'
        params['is_dst'] = '1'
        response = self.app.post(url_for(controller='maintenances', action='schedule', id=3),
                params=params)
        self.assert_(response.body)
        this_maint = db_sess.query(ScheduledMaintenance).get(3)
        self.assertEqual(this_maint.services[0].start_time,target_maintcal_datetime)

    def test_schedule_updated_notes(self):
        """ This tests simulates the user canceling the confirmation step
            and updating their notes.
        """
        self.mockTicketAddMessage()
        # start five hours from now
        params = self._getNowAsDict(add_hours=5)
        params['description'] = 'This is a description'
        params['tzname'] = 'UTC'
        params['is_dst'] = '0'
        response = self.app.post(url_for(controller='maintenances', action='schedule', id=3),
                params=params)
        
        service_4_pre = db_sess.query(ScheduledService).get(4)
        service_4_start_time = service_4_pre.start_time

        params = self._getNowAsDict(add_hours=5)
        params['description'] = 'This is not a description'
        params['tzname'] = 'UTC'
        params['is_dst'] = '0'

        response = self.app.post(url_for(controller='maintenances', action='schedule', id=3),
                params=params)
        this_maintenance = db_sess.query(ScheduledMaintenance).get(3)
        service_4_post = db_sess.query(ScheduledService).get(4)
        self.assertEqual(service_4_start_time,service_4_post.start_time)
        self.assertEqual(this_maintenance.general_description,
                'This is not a description')


    def test_schedule_change_contact(self):
        self.mockTicketAddMessage()
        # start five hours from now
        params = self._getNowAsDict(add_hours=5)
        params['contact'] = 'john.doe'
        params['tzname'] = 'UTC'
        params['is_dst'] = '0'
        response = self.app.post(url_for(controller='maintenances', action='schedule', id=3),
                params=params)


    def test_checkValidUserName(self):
        response= self.app.post(url_for(controller='maintenances', action='checkValidUserName'),
                params={'user_string': 'bob.racker'})
        self.assertEqual(response.body, '2')
