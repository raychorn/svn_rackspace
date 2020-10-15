from maintcal.tests.lib import url_for, MaintcalFunctionalTest

import simplejson
from datetime import datetime, timedelta
import time

from pylons import config

from maintcal.model import db_sess
from maintcal.lib import core_xmlrpc
from maintcal.lib.py2extjson import py2extjson
from maintcal.model import db_sess,Calendar 
from maintcal.tests.data.data_helper import server_names_to_ids, calendar_names_to_ids

import xmlrpclib
from pprint import pprint
from paste.util.multidict import UnicodeMultiDict,MultiDict

from urllib import urlencode

class TestMcalendarsController(MaintcalFunctionalTest):

    def local_setup(self):
        MaintcalFunctionalTest.local_setup(self)
        self.mockAuthToken()
        self.mockServerGetDetailsByComputers()

    def local_teardown(self):
        MaintcalFunctionalTest.local_teardown(self)
 
    def test_index(self):
        response = self.app.get(url_for(controller='mcalendars'))
        # Test response...
    
    def test_show_json(self):
        response = self.app.get(url_for(controller='mcalendars', action='show', id=1, format='json'))
        self.assertEqual(response.status, 200)
        
        cal = simplejson.loads(response.body)
        self.assertEqual(cal["name"], "SAT1")
        self.assertEqual(cal["description"], "SAT1 Testing Calendar")
        self.assertEqual(cal["tckt_queue_id"], 1)
        self.assertEqual(cal["active"], True)

    def test_show_json_one(self):
        response = self.app.post('/calendars/show_calendar_info.json',
            params = {
                'admin_console' : True,
                'allData'       : True,
                'calendars'     : 1})
        self.assertEqual(response.status, 200)
        
        cal = simplejson.loads(response.body)
        self.assertEqual(cal['rows'][0].keys(),['1'])
        self.assertEqual(cal['rows'][0]['1']["name"], "SAT1")
        self.assertEqual(cal['rows'][0]['1']["description"], "SAT1 Testing Calendar")
        self.assertEqual(cal['rows'][0]['1']["tckt_queue_id"], 1)
        self.assertEqual(cal['rows'][0]['1']["active"], True)

    def test_show_json_all(self):
        response = self.app.post('/calendars/show_calendar_info.json',
            params = {
                'admin_console' : True,
                'allData'       : True})
        self.assertEqual(response.status, 200)
        
        cal = simplejson.loads(response.body)
        self.assertEqual(cal['rows'][0]['1']["name"], "SAT1")
        self.assertEqual(cal['rows'][0]['1']["description"], "SAT1 Testing Calendar")
        self.assertEqual(cal['rows'][0]['2']["name"], "Managed Linux")
        self.assertEqual(cal['rows'][0]['3']["name"], "Intensive Windows")

    def test_selector_good_json(self):
        self.dh.insertTestComputerByName('managed_linux_one')
        self.assertSelectedCalendars(
                {'service_id':2, 
                 'servers':server_names_to_ids('managed_linux_one')},
                calendar_names_to_ids('Managed Linux', 'DFW1', 'Managed Backup'))


    def test_selector_good_only_devices_json(self):
        self.dh.insertTestComputerByName('managed_linux_one')
        self.assertNoSelectedCalendars(
                {'servers':server_names_to_ids('managed_linux_one')})

        
    def test_selector_bad_service_type(self):
        response = self.app.post('/calendars/selector.json',
            params = {'service_id' : 99999,
                      'servers' : 1},
            status=500)
        self.assert500(response, 'Invalid Service Type Id')

    def test_selector_bad_server_check(self):
        """Test that a bogus computer number fails validation."""
        response = self.app.post('/calendars/selector.json',
            params = {'service_id' : 2,
                      'servers' : 1},
            status=400)
        self.assert400(response, 'No valid devices were found.')

    def test_selector_invalid_service_id(self):
        response = self.app.post('/calendars/selector.json',
            params = {'service_id' : 'bobo_the_service_type',
                      'servers' : 110912},
                      status=500)
        self.assert500(response, 'Service Type Id must be a number.')

    def test_selector_no_post(self):
        response = self.app.get('/calendars/selector.json',status=400)
        self.assert400(response, 'This method accepts only POSTs')

    def test_selector_no_post_params(self):
        response = self.app.post('/calendars/selector.json',
                params={},status=400)
        self.assert400(response, 'No devices were selected.')

    def test_update_bad_cal_id(self):
        response = self.app.post('/calendars/update/200', status=400)
        self.assert400(response,'No such calendar with id 200')

    def test_update_bad_params(self):
        response = self.app.post('/calendars/update/1',
            params = {'service_id' : 'bobo_the_service_type',
                      'servers' : 110912},
                      status=400)

        self.assert400(response,'This resource requires a valid parameter for a calendar update')
    def test_update_single_val(self):
        response = self.app.post('/calendars/update/1',
            params = {'time_before_ticket_refresh' : '0.5'})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, '1')

    def test_update_multiple_vals(self):
        response = self.app.post('/calendars/update/1',
            params = {
                'name'     : 'New DFW1 Calendar',
                'timezone' : 'Europe/London',
                'time_before_ticket_refresh' : '0.5'})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, '1')

    def test_update_all_vals(self):
        response = self.app.post('/calendars/update/2',
            params = {
                'name'                      : "My New Calendar",
                'description'               : "My New Calendar",
                'tckt_queue_id'             : '26',
                'active'                    : 'true', 
                'timezone'                  : 'America/Chicago',
                'new_ticket_queue_id'       : '26',
                'new_ticket_category_id'    : '1035',
                'new_ticket_status_id'      : '1',
                'time_before_ticket_refresh': '1',
                'refresh_ticket_assignment' : 'true',
                'refresh_ticket_queue_id'   : '26',
                'refresh_category_id'       : '1035',
                'refresh_status_id'         : '1',
                'hold_tentative_time'       : '1'
            })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, '2')
        # check to see if the values 'stuck'
        cal = db_sess.query(Calendar).get(2)
        self.assertEqual(cal.name,'My New Calendar')
        self.assertEqual(cal.time_before_ticket_refresh,timedelta(minutes=60))
