import time

from maintcal.model.MaintcalModel import MaintcalModel
from maintcal.model.AvailableDefaults import ConsecutiveDefaultsException, QuantaBoundsException
from maintcal.lib.date import python_date_to_tuple
from datetime import date
from maintcal.lib.times_available import granularity_in_minutes

class StaleExceptionsException(Exception) : pass

class AvailableExceptions(MaintcalModel):
    
    @classmethod
    def fromJsDict(cls,calendar_id=None,exception_date=None,start_minutes=0,end_minutes=0,work_units=0,comments=":"):
        # JS gives a "work_units" which is in hours

        minutes = work_units * 60
        work_units_in_quanta = int(minutes / granularity_in_minutes())

        ae = AvailableExceptions()
        ae.calendar_id = calendar_id
        # Handle passing in a datetime or a date
        try:
            ae.exception_date = exception_date.date()
        except:
            ae.exception_date = exception_date
        ae.start_minutes = start_minutes
        ae.end_minutes = end_minutes
        ae.work_units_in_quanta = work_units_in_quanta
        ae.comments = comments
        return ae

    def _get_app_items(self):

        return {'exception_date' : self.exception_date,
                'start_minutes'  : self.start_minutes,
                'end_minutes'    : self.end_minutes,
                'work_units_in_quanta'     : self.work_units_in_quanta,
                'comments'       : self.comments }


    def match_period(self,period):
        return period.items() == self._get_app_items().items()
        
    def toJsDict(self):
        output = {}
        keys = self.__dict__.keys()
        for k in keys:
            if k.startswith("_"):
                continue
            if k == ('creation_date'):
                continue
            if k == ('modification_date'):
                # this will be a 'local' timestamp NOT UTC or zoned. 
                output['last_modified'] = int(time.mktime(self.modification_date.timetuple()))
                continue    
            if k == ('exception_date'):
                output['exception_date'] = python_date_to_tuple(self.exception_date)
                continue
            if k == ('work_units_in_quanta'):
                # Convert to hours for the UI
                output['work_units'] = self.work_units_in_quanta / 2.0
                continue
            output[k] = self.__dict__[k]

        return output 

