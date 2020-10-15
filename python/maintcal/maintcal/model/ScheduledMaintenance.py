
from datetime import timedelta
from pylons import config, request

import maintcal
from ChangeLog import MaintenanceChangeLog
from maintcal.model import db_sess

from maintcal.model.MaintcalModel import MaintcalModel
from maintcal.lib.date import seconds_to_hours, timedelta_to_total_seconds
from maintcal.lib.times_available import granularity_in_minutes

class ScheduledMaintenance(MaintcalModel):
    class State(object):

        TEMPORARY = 1
        TENTATIVE = 2
        SCHEDULED = 3
        CANCELED = 4
        COMPLETED = 5

        states = { TEMPORARY: "Temporary",
                   TENTATIVE: "Tentative",
                   SCHEDULED: "Scheduled",
                   CANCELED: "Canceled",
                   COMPLETED: "Completed"}
        
        def __init__(self, state_number):
            if not isinstance(state_number, int):
                raise TypeError, "State identifier must be 'int'"
            if not state_number in self.states.keys():
                raise ValueError, "No such state with id %s" % state_number
            self.id = state_number
            self.name = self.states[state_number]

        def __str__(self):
            return self.name

        def __int__(self):
            return self.id
    
    def __init__(self, ticket=''):
        self.master_ticket = ticket
        
        self.state_id = self.State.TEMPORARY
        self.general_description = u""
        self.billing_text = u""
        self.additional_duration = timedelta(0)
        self.service_type_id = None
        self.contact_id = None

    def total_duration(self):
        """ This is the length of the service type for this maintenance
            plus any additional duration that was specified for this mainteance.
            
            Note that the type of the return value is a timedelta.
        """
        total_duration = self.service_type.length + self.additional_duration
        return total_duration
   
    def total_duration_in_quanta(self):
        seconds = timedelta_to_total_seconds(self.total_duration())
        minutes = seconds / 60
        quanta = minutes / granularity_in_minutes()
        return quanta
 
    def __getattr__(self, attr):
        if attr=='state':
            self.state = self.State(self.state_id)
            return self.state
        if attr=='maintenance_category':
            if self.service_type:
                return self.service_type.maintenance_category
            else:
                return None
        if attr=='servers':
            rservers = set()
            for service in self.services:
                rservers.update(service.servers)
            return list(rservers)
        if attr=='length':
            return ((self.service_type and self.service_type.length) or timedelta(0)) + self.additional_duration
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
                MaintenanceChangeLog(self.id,
                                     contact = username,
                                     field = name,
                                     old_value = "%s" % unicode(self.__dict__[name]),
                                     new_value = "%s" % unicode(value)))
        object.__setattr__(self, name, value)
    
    # Methods for changing the state
    def cancel(self):
        for serv in self.services:
            serv.cancel()
        self.state_id = self.State.CANCELED
        if 'state' in self.__dict__.keys():
            self.__delattr__('state')
    
    def request(self):
        self.state_id = self.State.TENTATIVE
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
    
    def toDict(self):
        return { "id": self.id,
                  "general_description": self.general_description,
                  "master_ticket": self.master_ticket,
                  "expedite": self.expedite,
                  "service_type": str(self.service_type or u''),
                  "service_type_id": self.service_type_id,
                  "state": str(self.state or ''),
                  "state_id": int(self.state),
                  "maintenance_category": str(self.maintenance_category or u''),
                  "maintenance_category_id": (self.maintenance_category and int(self.maintenance_category)) or None,
                  "contact": str(self.contact or ''),
                  "contact_id": self.contact_id,
                  "additional_duration": str(self.additional_duration),
                  "notify_customer_before": bool(self.notify_customer_before),
                  "notify_customer_after": bool(self.notify_customer_after),
                  "notify_customer_name": str(self.notify_customer_name or u''),
                  "notify_customer_info": str(self.notify_customer_info or u''),
                  "notify_customer_department": str(self.notify_customer_department or u''),
                  "notify_customer_before_log": str(self.notify_customer_before_log or u''),
                  "notify_customer_after_log": str(self.notify_customer_after_log or u''),
                  "servers": [[
                      s.id,
                      ''.join((config['core.server_url'],str(s.id))),
                      ''.join((config['core.url'],s.icon or u'')),
                      s.name,
                      s.os_type
                      ] for s in self.servers],
                  "account_id": self.account_id
        }


    @classmethod
    def stale_maintenances(cls):
        """Return all stale maintenances"""
        old_maints_query = db_sess.query(ScheduledMaintenance)
        # New maintenances are Temporary
        old_maints_query = old_maints_query.filter('state_id in (%s,%s)' % \
                    (ScheduledMaintenance.State.TEMPORARY, ScheduledMaintenance.State.TENTATIVE))
        old_maints_query = old_maints_query.filter("creation_date < now() - interval '2 hours'")
        
        old_maints = old_maints_query.all()
        return old_maints
