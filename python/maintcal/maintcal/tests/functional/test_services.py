from maintcal.tests.lib import url_for, MaintcalFunctionalTest
import simplejson
from datetime import datetime

from maintcal.lib.base import config
from maintcal.model import db_sess, ScheduledService

class TestServicesController(MaintcalFunctionalTest):

    def test_index_maintenance_auth(self):
        """Passing in a maintenance ID as a parameter should return all services for that maintenance."""
        self.broken_test(); return
        response = self.app.get(url_for(controller='services', format='json'), params={'maintenance' : 1, 'tzname': 'UTC'})
        self.assertEqual(response.status, 200)
        #service_list = simplejson.loads(response.body)
        #print service_list 
        #self.assertEqual(len(service_list['rows']), 3)
        #self.assert_(1 in s['id'] for s in service_list)

    def test_index_calendar(self):
        self.mockTicketGetInfoForTickets()
        response = self.app.get(url_for(controller='services', format='json'), params={'calendar':2, 'tzname': 'UTC'})
        self.assertEqual(response.status, 200)
        response_services = simplejson.loads(response.body)
        
        self.assertEqual(len(response_services['rows']),3)
        self.assertEqual(set([u'2',u'3',u'5']),set([s['id'] for s in response_services['rows']]))

    def test_index_bad_calendar(self):
        self.broken_test(); return
        response = self.app.get(url_for(controller='services', format='json'), params={'calendar':2000, 'tzname': 'UTC'})
        self.assertEqual(response.status, 200)
        response_services = simplejson.loads(response.body)
        
        self.assertEqual(len(response_services['rows']),0)
    
    
    def test_index_time_range(self):
        """Passing a specified time range should return services scheduled for that time range."""
        self.broken_test(); return
        start_time = datetime(2008, 1, 10, 8)
        end_time = datetime(2008, 1, 10, 16)
        response = self.app.get(url_for(controller='services', format='json'),
                                params={'start_year' : 2008,
                                        'start_month' : 1,
                                        'start_day' : 10,
                                        'tzname': 'UTC'})
        service_list = simplejson.loads(response.body)
        
        self.assertEqual(len(service_list['rows']), 2)
        self.assert_(1 in s['id'] for s in service_list)


    def test_index_time_range_with_tz(self):
        """Passing a specified time range should return services scheduled for that time range."""
        self.broken_test(); return
        start_time = datetime(2008, 1, 10, 8)
        end_time = datetime(2008, 1, 10, 16)
        response = self.app.get(url_for(controller='services', format='json'),
                                params={'start_year' : 2008,
                                        'start_month' : 1,
                                        'start_day' : 10,
                                        'tzname' : 'America%2FChicago'})
        service_list = simplejson.loads(response.body)
        
        self.assertEqual(len(service_list['rows']), 2)
        self.assert_(1 in s['id'] for s in service_list)

    def test_index_bad_month(self):
        response = self.app.get(url_for(controller='services', format='json'),
                                params={'start_year' : 2008,
                                        'start_month' : 'A'
                                        },status=400)

    def test_index_bad_day(self):
        response = self.app.get(url_for(controller='services', format='json'),
                                params={'start_year' : 2008,
                                        'start_month' : 1,
                                        'start_day' : 'B'
                                        },status=400)

    def test_index_sjson(self):
        self.mockTicketGetInfoForTickets()
        response = self.app.get(url_for(controller='services',format='sjson'),
                                params={'calendar' : 2,
                                        'start_year' : 2008,
                                        'start_month' : 1,
                                        'tzname' : 'UTC'})

        self.assertEqual(response.status,200)

        sjson_services = simplejson.loads(response.body)
        self.assertEqual(set([u"None",u"Cabinet Migration"]),
                         set([s[2] for s in sjson_services]))

    def test_show(self):
        self.broken_test(); return
        response = self.app.get(url_for(controller='services', action='show',id=1, tzname='UTC'))
        self.assertEqual(response.status,200)
        self.assertEqual(response.body[:22],'{"recurrence_id": null')
    
    def test_show_json(self):
        self.broken_test(); return

        response = self.app.get(url_for(controller='services', action='show', id=1, format='json', tzname='UTC'))
        
        self.assertEqual(response.status, 200)
        
        service = simplejson.loads(response.body)
        self.assertEqual(service["description"], "Rerack server")
        self.assertEqual(service["ticket"], '080112-00443')
        #self.assertEqual(service["date_assigned"], "2008-01-01")
        #self.assertEqual(service["special_instructions"], 'handle with care')
        #self.assertEqual(service["contact"], 'bob.racker')
        self.assertEqual(service["contact_id"], 1)
        #self.assertEqual(service["start_time"], "2008-01-10 12:00:00")
        #self.assertEqual(service["end_time"], "2008-01-10 14:00:00")
        self.assertEqual(service["calendar"], "SAT1")
        self.assertEqual(service["calendar_id"], 1)
        self.assertEqual(service["maintenance_id"], 1)
        self.assert_(110912 in [s[1] for s in service["servers"]], "Server 1 should be in server list")
        self.assert_(110945 in [s[1] for s in service["servers"]], "Server 3 should be in server list")
        self.assertEqual( service['date_assigned_time_tuple'],[0, 0, 0, 0, 0, 0, 0, u'UTC', u'UTC'] )
        self.assertEqual( service['start_time_time_tuple'], [2008, 1, 10, 12, 0, 0, 0, u'UTC', u'UTC'] )
        self.assertEqual( service['end_time_time_tuple'], [2008, 1, 10, 14, 0, 0, 0, u'UTC', u'UTC'] )

    def test_bad_show(self):
        response = self.app.get(url_for(controller='services', action='show',id=2000, format='json', tzname='UTC'),status=404)

    def test_edit(self):
        """ This should successfully do nothing """
        response = self.app.get(url_for(controller='services', action='edit'))
        self.assertEqual(response.status,200)
    
    def test_create(self):
        """ This should successfully do nothing """
        response = self.app.get(url_for(controller='services', action='create'))
        self.assertEqual(response.status, 200)

    def test_new(self):
        """ This should successfully do nothing """
        response = self.app.get(url_for(controller='services', action='new'))
        self.assertEqual(response.status, 200)

    
    def test_update_json(self):
        response = self.app.post('/services/update/1', params={'description' : 'Change the world'})
        service = db_sess.query(ScheduledService).get(1)
        self.assertEqual(service.description, 'Change the world')

    def test_bad_update(self):
        response = self.app.get(url_for(controller='services', action='update',id=2000, format='json', tzname='UTC'),status=404)

    def test_delete(self):
        # This is testing an action that does nothing
        # in fact, this test verifies that you can call the url
        # but the browser will probably not be sending an HTTP DELETE
        response = self.app.delete(url_for(controller='services', action='delete',id=6, format='json'),status=200)
    
    def test_complete(self):
        """ Complete a scheduled service.  """
        self.mockAuthToken()
        self.mockTicketSystemUpdateTicketStatusType()
        self.mockTicketAddMessage()
        response = self.app.post(url_for(controller='services', action='complete', id=1))
        service = db_sess.query(ScheduledService).get(1)
        self.assertEqual(service.state_id, ScheduledService.State.COMPLETED)
        return_dict = simplejson.loads(response.body)
        self.assertEqual(response.status,200)
        self.assertEqual(return_dict['status_type'],'service')
        self.assertEqual(return_dict['status_id'],5)
        self.assertEqual(return_dict['status'],'Completed')

    def test_bad_complete_canceled(self):
         # modify the ScheduledService object to be already canceled.
        this_service = db_sess.query(ScheduledService).get(1)
        this_service.cancel()
        # do the cancel request
        response = self.app.post(url_for(controller='services', action='complete', id=1),status=400)

    def test_bad_complete_completed(self):
         # modify the ScheduledService object to be already canceled.
        this_service = db_sess.query(ScheduledService).get(1)
        this_service.complete()
        # do the cancel request
        response = self.app.post(url_for(controller='services', action='complete', id=1),status=400)

    def test_complete_last_service(self):
        self.mockAuthToken()
        self.mockTicketSystemUpdateTicketStatusType()
        self.mockTicketAddMessage()
        response = self.app.post(url_for(controller='services', action='complete', id=3))
        service = db_sess.query(ScheduledService).get(3)
        self.assertEqual(service.state_id, ScheduledService.State.COMPLETED)
        self.assertEqual(service.maintenance.id,2)
        return_dict = simplejson.loads(response.body)
        self.assertEqual(response.status,200)
        self.assertEqual(return_dict['status_type'],'maintenance')
        self.assertEqual(return_dict['status_id'],5)
        self.assertEqual(return_dict['status'],'Completed')

    def test_cancel_invalid_method(self):
        response = self.app.get(url_for(controller='services', action='cancel',id=1),status=400)

    def test_cancel_bad_service(self):
        response = self.app.post(url_for(controller='services', action='cancel',id=2000),status=404)

    def test_cancel_with_no_message(self):
        self.mockAuthToken()
        self.mockTicketSystemUpdateTicketStatusType()
        self.mockTicketAddMessage()

        service_id = 1
        service = db_sess.query(ScheduledService).get(service_id)
        self.assertNotEqual(service.state_id, ScheduledService.State.CANCELED)

        # 'reasons' is now required - As of 03/29/2012 generates a "KeyError"
        # if not present. Will need to refactor this to be a bit more 
        # 'corect' and appropraitely handle this error.
        response = self.app.post(url_for(controller='services', action='cancel', id=service_id), params={'reasons' : ''})

        service = db_sess.query(ScheduledService).get(service_id)
        self.assertEqual(service.state_id, ScheduledService.State.CANCELED)

    def test_cancel_message(self):
        self.mockAuthToken()
        self.mockTicketSystemUpdateTicketStatusType()
        self.mockTicketAddMessage()

        service_id = 1
        service = db_sess.query(ScheduledService).get(service_id)
        self.assertNotEqual(service.state_id, ScheduledService.State.CANCELED)

        response = self.app.post(url_for(controller='services', action='cancel', id=service_id), 
                params={'cancel_message':'This is the message',
                        'reasons'       : ''})

        service = db_sess.query(ScheduledService).get(service_id)
        self.assertEqual(service.state_id, ScheduledService.State.CANCELED)

    def test_cancel_last_service(self):
        # overload the functionality of this test by also testing to ensure
        # that CORE is not called on a service with no ticket.
        response = self.app.post(url_for(controller='services', action='cancel', id=6),params={'reasons' : ''})
        service = db_sess.query(ScheduledService).get(6)
        self.assertEqual(service.state_id, ScheduledService.State.CANCELED)
        self.assertEqual(service.maintenance.id,4)
        return_dict = simplejson.loads(response.body)
        self.assertEqual(response.status,200)
        self.assertEqual(return_dict['status_type'],'maintenance')
        self.assertEqual(return_dict['status_id'],4)
        self.assertEqual(return_dict['status'],'Canceled')


    def test_bad_cancel_canceled(self):
        # modify the ScheduledService object to be already canceled.
        this_service = db_sess.query(ScheduledService).get(1)
        this_service.cancel()
        # do the cancel request
        response = self.app.post(url_for(controller='services', action='cancel', id=1),status=400)

    def test_bad_cancel_completed(self):
        # modify the ScheduledService object to be already completed.
        this_service = db_sess.query(ScheduledService).get(1)
        this_service.complete()
        # do the cancel request
        response = self.app.post(url_for(controller='services', action='cancel', id=1),status=400)
