from maintcal.tests.lib import url_for, MaintcalFunctionalTest

import simplejson
from datetime import datetime, timedelta

from maintcal.lib import core_xmlrpc
from maintcal.model import db_sess
from maintcal.model import MaintenanceCategory, ServiceType, ScheduledMaintenance, ScheduledService
from maintcal.controllers.maintenances import MaintenancesController
from maintcal.lib.times_available.calculator import HTTP404Error, HTTP400Error

class TestMaintenancesTimesAvailableController(MaintcalFunctionalTest):

    def local_setup(self):
        MaintcalFunctionalTest.local_setup(self)

        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60, 24)

    def test_times_available(self):
        # TODO: make this thing set up proper defaults and overrides etc
        self.broken_test() ; return
        response = self.app.get(url_for(controller='maintenances', action='times_available', id=1),
                params={'start_year': 2038,
                'start_month' : 2,
                'start_day' : 1,
                'tzname' : 'UTC'})
        self.assert_(response.body)


    def test_times_available_with_day(self):
        self.broken_test() ; return
        response = self.app.get(url_for(controller='maintenances', action='times_available', id=1),
                params={'start_year': 2038,
                'start_month' : 1,
                'start_day' : 1,
                'tzname' : 'UTC'})
        # TODO: make this thing set up proper defaults and overrides etc
        self.assert_(response.body)
        times = simplejson.loads(response.body)
        #print times
        days = times.keys()
        days.sort()
        #self.assertEqual(days[0], "1")
        self.assertEqual(2, len(times[u"calendars"]))

    # Nate and Ryan have determined the UI should be able to query without needing to know what day it is.
    def test_times_available_without_day(self):
        self.broken_test() ; return
        # TODO: make this thing set up proper defaults and overrides etc
        response = self.app.get(url_for(controller='maintenances', action='times_available', id=3),
                params={'start_year': 2038,
                'start_month' : 1,
                'tzname' : 'UTC'}, status=200)
        self.assertEqual( response.status , 200 )

    def test_times_available_with_times_available(self):
        self.broken_test() ; return
        # TODO: make this thing set up proper defaults and overrides etc
        response = self.app.get(url_for(controller='maintenances', action='times_available', id=3),
                params={'start_year': 2038,
                'start_month' : 3,
                'start_day' : 1,
                'tzname' : 'UTC'})
        self.assert_(response.body)
        times = simplejson.loads(response.body)
        # TODO: make this thing set up proper defaults and overrides etc
        #print times
        days = times.keys()
        days.sort()
        #self.assertEqual(days[0], "1")
        self.assertEqual(2, len(times[u"calendars"]))
        #self.assertEqual(times[u"calendars"], [])

    def test_times_available_no_tzinfo(self):
        # TODO: make this thing set up proper defaults and overrides etc
        response = self.app.get(url_for(controller='maintenances', action='times_available', id=3),
                params={'start_year': 2038,
                'start_month' : 3,
                'start_day' : 1, }, status=400)
        self.assertEqual( response.status , 400 )
        self.assertTrue( "No timezone information supplied" in response.body, response.body )

    def test_times_available_no_start_time(self):
        # TODO: make this thing set up proper defaults and overrides etc
        response = self.app.get(url_for(controller='maintenances', action='times_available', id=3),
                params={'start_year': 2038,
                'tzname': 'UTC', }, status=400)
        self.assertEqual( response.status , 400 )
        self.assertTrue( "No start time submitted" in response.body, response.body )

    def test_times_available_no_start_time_not_ints(self):
        # TODO: make this thing set up proper defaults and overrides etc
        response = self.app.get(url_for(controller='maintenances', action='times_available', id=3),
                params={'start_year': 2038,
                'start_month' : 3,
                'start_day' : 'blah',
                'tzname' : 'UTC'}, status=404)
        self.assertEqual( response.status , 404 )
        self.assertTrue( "must be valid integer representable values" in response.body, response.body )

    def test_times_available_london_to_new_york(self):
        """
            Test case where tzname is Europe/London going to schedule into a DC in US/Eastern aka. America/New_York
            IAD2 ( and IAD1 ) are reporting intermittent overbooking of maintenances 
        """
        self.dh.insertAvailableDefault(3, 0, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(3, 1, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(3, 2, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(3, 3, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(3, 4, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(3, 5, 0*60, 24*60, 24)
        self.dh.insertAvailableDefault(3, 6, 0*60, 24*60, 24)


        response = self.app.get(url_for(controller='maintenances', action='times_available', id=5),
                params={'start_year': 2010,
                'start_month' : 6,
                'tzname' : 'Europe%2FLondon'}, status=200)
        #print response.body
        self.assertEqual( response.status , 200 )

    def test_times_available_not_future_date(self):
        self.broken_test() ; return
        # TODO: make this thing set up proper defaults and overrides etc
        response = self.app.get(url_for(controller='maintenances', action='times_available', id=3),
                params={'start_year': 1980,
                'start_month' : 3,
                'start_day' : 1,
                'tzname' : 'UTC'}, status=200)
        self.assertEqual( response.status , 200 )


