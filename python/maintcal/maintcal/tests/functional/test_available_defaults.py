from maintcal.tests.lib import url_for, MaintcalFunctionalTest
import simplejson

class TestAvailableDefaultsController(MaintcalFunctionalTest):

    def test_index(self):
        # Friday
        python_dow = 4
        js_dow = u'5'

        self.dh.insertAvailableDefault(1, python_dow, 0*60, 12*60 - 1, 12)
        self.dh.insertAvailableDefault(1, python_dow, 12*60, 24*60 - 1, 24)

        response = self.app.get('/available_defaults/1')
        self.assertEqual(response.status, 200)
        defaults = simplejson.loads(response.body)['rows'][0][js_dow]
        self.assertEqual(2, len(defaults))


    def test_update(self):

        # Friday
        python_dow = 4
        js_dow = u'5'
        self.dh.insertAvailableDefault(1, python_dow, 0*60, 12*60 - 1, 24)
        self.dh.insertAvailableDefault(1, python_dow, 12*60, 24*60 - 1, 24)

        # Gets a current list
        response = self.app.get('/available_defaults/1')
        self.assertEqual(response.status, 200)
        results = simplejson.loads(response.body)
        defaults = results['rows'][0][js_dow]

        self.assertEqual(2, len(defaults))
        self.assertEqual(24, defaults[0]['work_units'])
        self.assertEqual(24, defaults[1]['work_units'])

        # update the values
        default_zero = {'start_minutes':0, 'end_minutes':60, 'work_units': 2, 'comments': 'This is a test comment'}
        default_one = {'start_minutes':60, 'end_minutes':120, 'work_units': 2, 'comments': ''}

        calendar_data_json = simplejson.dumps({js_dow: [default_zero, default_one], 'last_modified': defaults[0]['last_modified'] })
        params = {'calendar_data': calendar_data_json}

        active_response = self.app.post('/available_defaults/1/update', params=params)

        # Check the results
        response = self.app.get('/available_defaults/1')
        self.assertEqual(response.status, 200)
        defaults = simplejson.loads(response.body)['rows'][0][js_dow]
        self.assertEqual(2, len(defaults))
        self.assertEqual(2, defaults[0]['work_units'])
        self.assertEqual(2, defaults[1]['work_units'])
        self.assertTrue(bool(defaults[0]['comments']))
        self.assertFalse(bool(defaults[1]['comments']))
        
    def test_silently_kill_zero_length_period(self):
        """
        Silently remove a period that has a zero duration in minutes. 
        """

        # Friday
        python_dow = 4
        js_dow = u'5'

        self.dh.insertAvailableDefault(1, python_dow, 0*60,  12*60 - 1, 24)
        self.dh.insertAvailableDefault(1, python_dow, 12*60, 24*60 - 1, 24)

        # Gets a current list
        response = self.app.get('/available_defaults/1')
        self.assertEqual(response.status, 200)
        results = simplejson.loads(response.body)
        defaults = results['rows'][0][js_dow]

        self.assertEqual(2, len(defaults))
        self.assertEqual(24, defaults[0]['work_units'])
        self.assertEqual(24, defaults[1]['work_units'])

        # update the values
        default_zero = {'start_minutes':0, 'end_minutes':60, 'work_units': 2, 'comments': 'This is a test comment'}
        default_one = {'start_minutes':60, 'end_minutes':120, 'work_units': 2, 'comments': ''}

        # This will break the calendar if it goes to the db
        default_two = {'start_minutes':120, 'end_minutes':120, 'work_units': 2, 'comments': 'This is a horrible fail'}

        calendar_data_json = simplejson.dumps({js_dow: [default_zero, default_one, default_two], 'last_modified': defaults[0]['last_modified'] })
        params = {'calendar_data': calendar_data_json}

        active_response = self.app.post('/available_defaults/1/update', params=params)

        # Check the results
        response = self.app.get('/available_defaults/1')
        self.assertEqual(response.status, 200)
        defaults = simplejson.loads(response.body)['rows'][0][js_dow]
        self.assertEqual(2, len(defaults))
        self.assertEqual(2, defaults[0]['work_units'])
        self.assertEqual(2, defaults[1]['work_units'])

        self.assertEqual('This is a test comment', defaults[0]['comments'])
        self.assertFalse(bool(defaults[1]['comments']))
        


