from maintcal.tests.lib import url_for, MaintcalFunctionalTest

import simplejson
from datetime import datetime

from maintcal.lib.base import config
from maintcal.model import db_sess


class TestSchedulesController(MaintcalFunctionalTest):

    def test_index(self):
        response = self.app.get(url_for(controller='schedules'))
        # Test response...
        self.assertEqual(response.status, 200)

    def test_set_available_defaults_for_day(self):
        pass

