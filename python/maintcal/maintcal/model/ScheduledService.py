from pylons import config, request
from datetime import datetime, timedelta

import maintcal
from ChangeLog import ServiceChangeLog
from ScheduledServiceReason import ScheduledServiceReason
from maintcal.model import db_sess
from maintcal.model.MaintcalModel import MaintcalModel
from maintcal.lib.date import seconds_to_hours
from maintcal.lib.date import timedelta_to_total_seconds
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from maintcal.lib.date.timezone_renderer import TimezoneRenderer
from maintcal.lib.times_available import granularity_in_minutes 

class ScheduledService(MaintcalModel):
    class State(object):
        TENTATIVE = 1
        SCHEDULED = 2
        CANCELED = 4
        COMPLETED = 5
        PAST_DUE = 6
        COMPLETED_WITH_ISSUES = 7
        UNSUCCESSFUL = 8

        state_names = {
            TENTATIVE: 'Tentative',
            SCHEDULED: 'Scheduled',
            CANCELED: 'Canceled',
            COMPLETED: 'Completed',
            PAST_DUE: 'Past Due',
            COMPLETED_WITH_ISSUES: 'Completed With Issues',
            UNSUCCESSFUL: 'Failed',
            }
        def __init__(self, state_id):
            self.id = state_id
            self.name = self.state_names[state_id]

        def __str__(self):
            return self.name
    
    def __init__(self, description=u"", calendar=None, maintenance_id=None):
        self.calendar_id = calendar

        self.start_time = None
        self.end_time = None
        self.description = description
        self.scheduled_maintenance_id = maintenance_id
        self.special_instruction = None
        self.ticket_number = None
        self.servers = []
        self.state_id = self.State.TENTATIVE
        self.ticket_popped = False

    def __getattr__(self, attr):
        if attr=='state':
            if not self.state_id:
                return None
            self.state = self.State(self.state_id)
            return self.state
        if attr=='service_type':
            if self.maintenance and self.maintenance.service_type:
                return self.maintenance.service_type
            else:
                return None
        if attr=='maintenance_category':
            if self.service_type and self.service_type.maintenance_category:
                return self.service_type.maintenance_category
            else:
                return None
        if attr=='contact_id':
            if self.maintenance:
                return self.maintenance.contact_id
            else:
                return None
        if attr=='contact':
            if self.maintenance:
                return self.maintenance.contact
            else:
                return None
            
        raise AttributeError, "No such attribute '%s'" % attr
    
    def __setattr__(self, name, value):
        if config.get('enable_changelog') and 'id' in self.__dict__.keys() and self.__dict__['id'] and name in self.__dict__.keys():
            username = 'No contact'
            try:
                if request.environ and request.environ.get('beaker.session') and request.environ['beaker.session'].get('core.username'):
                    username = request.environ['beaker.session']['core.username']
            except TypeError:
                username = 'No contact'
            
            maintcal.model.db_sess.save(
                ServiceChangeLog(self.id,
                                     contact = username,
                                     field = name,
                                     old_value = "%s" % unicode(self.__dict__[name]),
                                     new_value = "%s" % unicode(value)))

        # Force start_time and end_time into maintcal_datetimes
        if name == 'start_time' and hasattr(value, "microsecond"):
            value = MaintcalDatetime.from_python_datetime(value)
        if name == 'end_time' and hasattr(value, "microsecond"):
            value = MaintcalDatetime.from_python_datetime(value)

        object.__setattr__(self, name, value)
    
    def cancel(self, reasons=None, feedback=None):
        if reasons:
            for reason in reasons.split(','):
                maintcal.model.db_sess.save(
                    ScheduledServiceReason(self.id, reason))
            
        if feedback:
            reason = 'Feedback'
            maintcal.model.db_sess.save(
                ScheduledServiceReason(self.id, reason, feedback))
            
        
        self.state_id = self.State.CANCELED
        if 'state' in self.__dict__.keys():
            self.__delattr__('state')
    
    def schedule(self):
        self.state_id = self.State.SCHEDULED
        if 'state' in self.__dict__.keys():
            self.__delattr__('state')
    
    def complete(self):
        self.state_id = self.State.COMPLETED
        if 'state' in self.__dict__.keys():
            self.__delattr__('state')

    def completeWithIssues(self, reasons, feedback=None):
        for reason in reasons.split(','):
            maintcal.model.db_sess.save(
                ScheduledServiceReason(self.id, reason))

        if feedback:
            reason = 'Feedback'
            maintcal.model.db_sess.save(
                ScheduledServiceReason(self.id, reason, feedback))

        self.state_id = self.State.COMPLETED_WITH_ISSUES
        if 'state' in self.__dict__.keys():
            self.__delattr__('state')

    def unsuccessful(self, reasons, feedback=None):
        for reason in reasons.split(','):
            maintcal.model.db_sess.save(
                ScheduledServiceReason(self.id, reason))

        if feedback:
            reason = 'Feedback'
            maintcal.model.db_sess.save(
                ScheduledServiceReason(self.id, reason, feedback))

        self.state_id = self.State.UNSUCCESSFUL
        if 'state' in self.__dict__.keys():
            self.__delattr__('state')

    def expire(self):
        self.state_id = self.State.PAST_DUE
        if 'state' in self.__dict__.keys():
            self.__delattr__('state')
    
    def toDict(self, timezone_name, show_server_info=False):
        """
        Convert this record to a dictionary.
        All datetimes will be converted to the timezone specified in timezone_name.
        """
        return_dict = {
            'id' : str(self.id),
            'general_description' : (self.maintenance and str(self.maintenance.general_description)) or None,
            'description' : str(self.description),
            'ticket' : self.ticket_number,
            'ticket_url' : '%s%s' % (config['core.ticket_url'],self.ticket_number),
            'account_id' : (self.maintenance and str(self.maintenance.account_id)) or None,
            'account_url' : '%s%s'%(config['core.account_url'],(self.maintenance and self.maintenance.account_id) or ''),
            'account_name' : (self.maintenance and str(self.maintenance.account_name)) or None,
            'contact' : (self.maintenance and str(self.maintenance.contact)) or None,
            'contact_id' : (self.contact and int(self.contact)) or None,
            'start_time' : str(self.start_time),
            'end_time' : str(self.end_time),
            'calendar' : str(self.calendar),
            'calendar_id' : self.calendar_id,
            'maintenance_id' : self.scheduled_maintenance_id,
            'state' : str(self.state),
            'state_id' : self.state_id,
            'recurrence_id': None,
            'service_type' : (self.maintenance and str(self.maintenance.service_type)) or None,
            'service_type_id' : (self.maintenance and self.maintenance.service_type_id) or None,
            'ticket_assignee' : self.ticket_assignee or None,
            'support_team' : self.support_team or None,
        }

        timezone_renderer = TimezoneRenderer(timezone_name)
        result = timezone_renderer.get_javascript_time_tuples([self.date_assigned, self.start_time, self.end_time])


        return_dict['date_assigned_time_tuple'] = result[0]
        return_dict['start_time_time_tuple'] = result[1]
        return_dict['end_time_time_tuple'] = result[2]

        sst = result[1]

        # If the year field is not zero, we assume that the date is defined
        if sst[0]:
            start_date = datetime(sst[0], sst[1], sst[2])
            return_dict['start_date'] = start_date.strftime("%Y%m%d")
        else:
            return_dict['start_date'] = ''

        if show_server_info:
            return_dict['servers'] = \
                [['%s%s'%(config['core.server_url'],str(s.id)),s.id,s.name,s.os_type] \
                for s in self.servers]
        return return_dict

    @classmethod
    def past_due_services(cls):
        """Returns all services that are SCHEDULED and have not been performed by the start_time."""
        past_due_query = db_sess.query(ScheduledService)
        past_due_query = past_due_query.filter_by(state_id=ScheduledService.State.SCHEDULED)
        past_due_query = past_due_query.filter("start_time < now() at time zone 'UTC'")
        past_due_services = past_due_query.all()
        return past_due_services

    #
    #   Times Available functionality
    #

    def overlaps(self, period):
        """Does this period overlap the current service?"""

        start_datetime = self.start_time.to_python_datetime()
        end_datetime = self.end_time.to_python_datetime()

        return period.start_time < end_datetime and period.end_time > start_datetime


    def periodsOverlappingService(self, periods):
        """ Filter a list of periods and only return those periods that
            occur inside of this service.
        """
        return [pd for pd in periods if self.overlaps(pd)]


    def quantaHandledByPeriod(self, period):
        """Returns the amount of quanta for the period that occur in the current service."""

        start_datetime = self.start_time.to_python_datetime()
        end_datetime = self.end_time.to_python_datetime()

        total_quanta = 0

        # Iterate through the quanta of the period, while the starting_quanta is less
        # than the ending quanta

        quanta_start_time = period.start_time
        while quanta_start_time < period.end_time:
            quanta_end_time = quanta_start_time + timedelta(minutes=granularity_in_minutes())

            if start_datetime <= quanta_start_time < end_datetime:
                if start_datetime < quanta_end_time <= end_datetime:
                    total_quanta = total_quanta + 1

            quanta_start_time = quanta_start_time + timedelta(minutes=granularity_in_minutes())

        return total_quanta


