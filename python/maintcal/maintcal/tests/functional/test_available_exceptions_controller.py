from maintcal.tests.lib import url_for, MaintcalFunctionalTest
from datetime import date
import simplejson

class TestAvailableExceptionsController(MaintcalFunctionalTest):

    def test_index(self):
        # Friday
        python_dow = 4

        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60 , 24)

        # add in an exception
        self.dh.insertAvailableException(1, date(2009, 9, 4), 0*60, 12*60 , 12)  
        self.dh.insertAvailableException(1, date(2009, 9, 4), 12*60, 24*60 , 24)

        params = {
            'start_year'  : 2009,
            'start_month' : 8,
            'start_day'   : 31,
            'end_year'    : 2009,
            'end_month'   : 9,
            'end_day'     : 5
        }
        response = self.app.post('/available_exceptions/1', params=params)
        self.assertEqual(response.status, 200)
        results = simplejson.loads(response.body)['rows'][0]
        self.assertEqual(len(results[u'2009,9,4']), 2)
        self.assertEqual(results[u'2009,9,4'][0][u'exception_date'],[2009, 9, 4])
        self.assertEqual(results[u'2009,9,4'][0][u'start_minutes'],0) 

    def test_index_bad_start(self):
         # Friday
        python_dow = 4

        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60 , 24)

        # add in an exception
        self.dh.insertAvailableException(1, date(2009, 9, 4), 0*60, 12*60 , 12)  
        self.dh.insertAvailableException(1, date(2009, 9, 4), 12*60, 24*60 , 24)

        params = {
            'start_year'  : 2009,
            'start_month' : 9,
            'start_day'   : 31,
            'end_year'    : 2009,
            'end_month'   : 9,
            'end_day'     : 5
        }
        response = self.app.post('/available_exceptions/1', params=params,status=400)
        self.assertEqual(response.status, 400)

    def test_index_end_before_start(self):
         # Friday
        python_dow = 4

        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60 , 24)

        # add in an exception
        self.dh.insertAvailableException(1, date(2009, 9, 4), 0*60, 12*60 , 12)  
        self.dh.insertAvailableException(1, date(2009, 9, 4), 12*60, 24*60 , 24)

        params = {
            'start_year'  : 2009,
            'start_month' : 9,
            'start_day'   : 30,
            'end_year'    : 2009,
            'end_month'   : 9,
            'end_day'     : 5
        }
        response = self.app.post('/available_exceptions/1', params=params,status=400)
        self.assertEqual(response.status, 400)

        
    def test_update_that_kills_exceptions(self):

        # Friday
        python_dow = 4
        js_dow = u'5'
        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60 , 24)


        # add in an exception
        self.dh.insertAvailableException(1, date(2009, 10, 27), 0*60, 12*60 , 12)  
        self.dh.insertAvailableException(1, date(2009, 10, 27), 12*60, 24*60 , 24)

        self.assertRecordCount('available_exceptions', 2)

        # last_modified is in epoch seconds, so we create records that were last modified in 1970
        calendar_data_json = """
            {
             "last_modified": 1,
             "2009,10,26":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,27":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,28":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,29":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,30":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,31":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,11,1" :[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}]
            }
        """

        params = {
            'admin_console': True,
            'calendar_data': calendar_data_json
        }

        response = self.post('/available_exceptions/1/update', params=params)
        self.assertEqual(response.status, 200)

        #defaults = simplejson.loads(response.body)['rows']

        self.assertRecordCount('available_exceptions', 0)

        #print defaults

        #self.assertEqual(2, len(defaults))
        #self.assertEqual(24, defaults[0]['work_units'])
        #self.assertEqual(24, defaults[1]['work_units'])

        # update the values
        #default_zero = {'start_minutes':0, 'end_minutes':60 - 1, 'work_units': 2, 'comments': 'This is a test comment'}
        #default_one = {'start_minutes':60, 'end_minutes':120 - 1, 'work_units': 2, 'comments': ''}

        #calendar_data_json = simplejson.dumps({js_dow: [default_zero, default_one]})
        #params = {'calendar_data': calendar_data_json}

        #active_response = self.app.post('/available_defaults/1/update', params=params)

        # Check the results
        #response = self.app.get('/available_defaults/1')
        #self.assertEqual(response.status, 200)
        #defaults = simplejson.loads(response.body)['rows'][0][js_dow]
        #self.assertEqual(2, len(defaults))
        #self.assertEqual(2, defaults[0]['work_units'])
        #self.assertEqual(2, defaults[1]['work_units'])
        #self.assertTrue(bool(defaults[0]['comments']))
        #self.assertFalse(bool(defaults[1]['comments']))
       

    def test_update_that_includes_zero_length_period(self):

        # Friday
        python_dow = 4
        js_dow = u'5'

        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60 , 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60 , 24)

        self.assertRecordCount('available_exceptions', 0)

        # last_modified is in epoch seconds, so we create records that were last modified in 1970

        calendar_data_json = """
            {
             "last_modified": 1,
             "2009,10,26":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,27":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,28":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,29":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,30":[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,10,31":[{"start_minutes":0,"end_minutes":1440,"work_units":4,"comments":""},{"start_minutes":1440,"end_minutes":1440,"work_units":24,"comments":""}],
             "2009,11,1" :[{"start_minutes":0,"end_minutes":1440,"work_units":24,"comments":""}]
            }
        """

        params = {
            'admin_console': True,
            'calendar_data': calendar_data_json
        }

        response = self.post('/available_exceptions/1/update', params=params)
        self.assertEqual(response.status, 200)

        #defaults = simplejson.loads(response.body)['rows']

        # The october 31 record should be created
        self.assertRecordCount('available_exceptions', 1)

        params = {
            'start_year'  : 2009,
            'start_month' : 8,
            'start_day'   : 31,
            'end_year'    : 2009,
            'end_month'   : 11,
            'end_day'     : 5
        }
 
        response = self.app.post('/available_exceptions/1', params=params)
        self.assertEqual(response.status, 200)
        results = simplejson.loads(response.body)['rows'][0]
        self.assertEqual(len(results[u'2009,10,31']), 1)
        self.assertEqual(results[u'2009,10,31'][0][u'exception_date'],[2009, 10, 31])
        self.assertEqual(results[u'2009,10,31'][0][u'start_minutes'],0) 
        self.assertEqual(results[u'2009,10,31'][0][u'end_minutes'],1440) 






