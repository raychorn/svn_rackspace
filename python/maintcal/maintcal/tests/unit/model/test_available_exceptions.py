from maintcal.tests.lib import MaintcalUnitTest

from maintcal.model import db_sess, ScheduledMaintenance, ServiceType, MaintenanceCategory
from maintcal.model import AvailableExceptions
from datetime import date

class TestAvailableExceptions(MaintcalUnitTest):

    def test_jsDict(self):
        ot = AvailableExceptions() 
        ot.calendar_id = 1
        ot.exception_date = date(2009, 9, 20)
        ot.start_minutes = 0*60
        ot.end_minutes = 8*60 - 1
        ot.work_units = 8
        
        self.assertEquals( ot.toJsDict(), 
                {'work_units': 8, 'end_minutes': 479, 'start_minutes': 0, 
                 'exception_date': (2009, 9, 20), 'calendar_id': 1} )


