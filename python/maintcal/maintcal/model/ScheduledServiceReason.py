from pylons import config, request
from datetime import datetime, timedelta

import maintcal
from maintcal.model import db_sess
from maintcal.model.MaintcalModel import MaintcalModel

class ScheduledServiceReason(MaintcalModel):
    def __init__(self, service, reason, feedback = None):
        self.service_id = service
        self.reason = reason
        self.feedback = feedback

    def __getattr__(self, attr):
        if attr=='service':
            if not self.service_id :
                return None
            self.state = self.ScheduledService(self.service_id)
            return self.state
        if attr=='reason':
            return self.reason
        if attr=='feedback':
            return self.feedback
            
        raise AttributeError, "No such attribute '%s'" % attr
    
    def toDict(self):
        return {
            'id' : self.id,
            'reason' : self.reason,
            'feedback' : self.feedback,
            'service_id' : self.service_id,
        }
