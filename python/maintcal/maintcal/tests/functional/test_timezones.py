from maintcal.tests.lib import url_for, MaintcalFunctionalTest

from datetime import datetime
import sys
import simplejson

class TestTimezonesController(MaintcalFunctionalTest):

    def test_offset_success(self):
        this_tz = 'America/Chicago'
        response = self.app.get(url_for(controller='timezones',action='offset'),
                                params={'tzname':this_tz})
        r1 = simplejson.loads(response.body)
        self.assert_(r1['offset_hours'] == -5 or r1['offset_hours'] == -6)

    def test_offset_error(self):
        t1 = 'jsdlfjsdl/ljsdflkjsd'
        response = self.app.get(url_for(controller='timezones',action='offset'),
                                params={'tzname':t1} ,status=404)
