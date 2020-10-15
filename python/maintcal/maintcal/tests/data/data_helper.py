"""
This class should provide an interface for all test data needs.

It should provide for test setup and teardown and other functionality
in one nice interface.

MaintcalTest should always have a member variable of self.dh
that is an instance of DataHelper.

"""
# NOTE: do NOT import generated_data.py into this file
#       This is because frozen_data.py imports generated_data.py and updates
#       the data structures inside of generated_data.py
#       Therefore we import frozen_data and use its copies of the data structures.
from maintcal.tests.data.frozen_data import computer_detail, server_names_to_ids, named_servers 
from maintcal.tests.data.frozen_data import test_calendars, calendars_by_name, calendar_names_to_ids
from maintcal.tests.data import data_fixtures

from maintcal.model import db_sess
from maintcal.model import metadata, engine, MaintenanceCategory, \
    ServiceType, Calendar, Contact, ScheduledMaintenance, \
    ScheduledService, Server, Selector, AvailableDefaults, AvailableExceptions

from maintcal.lib.times_available import granularity_in_minutes

class DataHelper(object):

    def insertTestComputer(self, computer_number):
        """Loads a test computer into the db and return the server object."""
        db_sess.begin_nested()
        server = Server.fromDict(computer_detail[computer_number])
        db_sess.add(server)
        db_sess.commit()
        return server


    def insertTestComputerByName(self, computer_name):
        """Loads a test computer into the db."""
        self.insertTestComputer(server_names_to_ids(computer_name)[0])


    def insertAvailableDefault(self, cal_id, dow, start_min, end_min, work_units_in_hours, comments=None):
        minutes = work_units_in_hours * 60
        work_units_in_quanta = int(minutes / granularity_in_minutes())

        # TODO: fix tests to pass in work units in quanta
        db_sess.begin_nested()
        dt = AvailableDefaults() 
        dt.calendar_id = cal_id
        dt.dow = dow
        dt.start_minutes = start_min
        dt.end_minutes = end_min
        dt.work_units_in_quanta = work_units_in_quanta
        dt.comments = comments
        db_sess.add(dt)
        db_sess.commit()
        return dt


    def insertAvailableException(self, cal_id, exception_date, start_min, end_min, work_units_in_hours, comments=None):
        minutes = work_units_in_hours * 60
        work_units_in_quanta = int(minutes / granularity_in_minutes())

        # TODO: fix tests to pass in work units in quanta
        db_sess.begin_nested()
        ot = AvailableExceptions() 
        ot.calendar_id = cal_id
        ot.exception_date = exception_date
        ot.start_minutes = start_min
        ot.end_minutes = end_min
        ot.work_units_in_quanta = work_units_in_quanta
        ot.comments = comments
        db_sess.add(ot)
        db_sess.commit()
        return ot


    def insertScheduledService(self, cal_id, start_time, end_time, scheduled_maintenance_id=None, state=False):
        db_sess.begin_nested()
        ss = ScheduledService() 
        ss.calendar_id = cal_id
        #ss.description = ''
        #ss.ticket_number = ''
        ss.start_time = start_time
        ss.end_time = end_time
        if scheduled_maintenance_id:
            ss.scheduled_maintenance_id = scheduled_maintenance_id 

        if not state:
            ss.state_id = 2
        else:
            ss.state_id = state

        #ss.ticked_popped = 0
        db_sess.add(ss)
        db_sess.commit()
        return ss 


    def define_calendar(self, name, description, ticket_queue=0, active=False, id=1, timezone=None):
        """Simple way to define a calendar and place it into test_calendars"""
        cal = Calendar(name, description, ticket_queue, active)
        cal.id = id
        if timezone:
            cal.timezone = timezone
        test_calendars[id] = cal
        calendars_by_name[cal.name] = cal.id


    def insertCalendars(self):
        """Defines and inserts all of the default test calendars"""
        self.define_calendar(u"SAT1", u"SAT1 Testing Calendar", 1, True, 1, 'UTC') 
        self.define_calendar(u"Managed Linux", u"Calendar for M Linux", 2, True, 2, 'America/Chicago')
        self.define_calendar(u"Intensive Windows", u"Calendar for Int Win", 3, True, 3, 'America/New_York')
        self.define_calendar(u"Managed Storage", u"Calendar for storage team", 4, True, 4, 'UTC')
        self.define_calendar(u"DFW1", u"DFW1 Testing Calendar", 5, True, 5, 'UTC')
        self.define_calendar(u"Managed Backup", u"Calendar for backup team", 6, True, 6, 'UTC')

        db_sess.begin_nested()
        for cal in test_calendars.values():
            db_sess.add(cal)
        #cal = db_sess.query(Calendar).get('1')
        db_sess.commit()
        #print cal


    def insert_data(self):
        """Wraps the real insert_data, but allows insert_data to call methods on this
        DataHelper instance."""
        data_fixtures.insert_data(self)

