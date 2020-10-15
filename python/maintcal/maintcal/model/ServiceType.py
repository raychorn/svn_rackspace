
from datetime import timedelta
from pylons import config, request

import maintcal
from maintcal.lib.date import timedelta2hours
from maintcal.lib.date import timedelta_to_total_seconds
from ChangeLog import ServiceTypeChangeLog
from maintcal.model.MaintcalModel import MaintcalModel

class ServiceType(MaintcalModel):
    def __init__(self, name=u'', description=u'', maintenance_category=0, length=None, lead_time=None):
        self.name = name
        self.description = description
        self.maintenance_category_id = maintenance_category
        self.length = length or timedelta(0)
        self.lead_time = lead_time or timedelta(0)
        self.active = True
    
    def __str__(self):
        return self.name
    
    def __int__(self):
        return self.id
    
    def __setattr__(self, name, value):
        if config.get('enable_changelog') and 'id' in self.__dict__.keys() and self.__dict__['id'] and name in self.__dict__.keys():
            username = 'No contact'
            try:
                if request.environ and request.environ.get('beaker.session') and request.environ['beaker.session'].get('core.username'):
                    username = request.environ['beaker.session']['core.username']
            except TypeError:
                username = 'No contact'
            
            maintcal.model.db_sess.save(
                ServiceTypeChangeLog(self.id,
                                     contact = username,
                                     field = name,
                                     old_value = "%s" % unicode(self.__dict__[name]),
                                     new_value = "%s" % unicode(value)))
        object.__setattr__(self, name, value)
    
    def toDict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            'active' : self.active,
            'length_seconds' : timedelta_to_total_seconds(self.length),
            'length_hours' : float(timedelta2hours(self.length)),
            'lead_time_seconds' : timedelta_to_total_seconds(self.lead_time),
            'lead_time_hours' : float(timedelta2hours(self.lead_time)),
            'maintenance_category' : str(self.maintenance_category or ''),
            'maintenance_category_id' :self.maintenance_category_id,
        }
