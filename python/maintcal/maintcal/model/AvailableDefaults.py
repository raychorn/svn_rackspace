"""
NOTE:

    We are going to store the available defaults in the db in the local time
    of the calendar, not in UTC.


"""
import time
import sys 
from maintcal.model.MaintcalModel import MaintcalModel
from maintcal.model import db_sess, Calendar
from maintcal.lib.times_available import granularity_in_minutes

class StaleDefaultsException(Exception) : pass

class ConsecutiveDefaultsException(Exception): pass

class QuantaBoundsException(Exception): pass

class AvailableDefaults(MaintcalModel):

    @classmethod
    def get_available_defaults_for_calendar(cls, calendar_id, js_dow = True):
        """
        Gets the available defaults for a specific calendar in a format
        useful for the admin UI.
        """
        defaults = db_sess.query(cls).filter_by(calendar_id=calendar_id).order_by(AvailableDefaults.start_minutes).all()
        results = {}

        for default in defaults:
            if js_dow:
                key = default.js_dow()
            else:
                key = default.dow
            if key not in results:
                results[key] = []
            results[key].append(default.toJsDict())
        return results

    @classmethod
    def update_available_defaults_for_calendar(cls, calendar_id, defaults):
        """
        Update the available defaults for a specific calendar in a format
        useful for the admin UI.
        """

        last_modified = defaults.get('last_modified')
        del defaults['last_modified']
        
        period_check_date = None
        for js_dow in defaults:
            js_dow_int = int(js_dow)
            defaults[js_dow]
            # js 0 is python date weekday of 6
            try:
                if js_dow_int == 0:
                    cls._update_available_defaults_for_dow(calendar_id, 6, defaults[js_dow],last_modified)
                else:
                    # otherwise we subtract 1
                    cls._update_available_defaults_for_dow(calendar_id, js_dow_int-1, defaults[js_dow],last_modified)

            except QuantaBoundsException:
                db_sess.rollback()
                raise QuantaBoundsException
            
            except ConsecutiveDefaultsException:
                db_sess.rollback()
                raise ConsecutiveDefaultsException

    @classmethod
    def _update_available_defaults_for_dow(cls, calendar_id, day_of_week, new_available_defaults,last_modified):
        """
        Update the available defaults for a specific day of the week
        """
        db_sess.begin_nested()

        def sortPeriodDefaults(x,y):
            return cmp(x.get('start_minutes'),y.get('start_minutes'))

        # sort periods to ensure all periods are consectutive.
        new_available_defaults.sort(sortPeriodDefaults)

        # Ensure that all periods are consectutive
        # ... AND ensure all periods are in quanta bounds
        check_date = None
        for adefault in new_available_defaults:
            if (adefault.get('start_minutes') % granularity_in_minutes()) or (adefault.get('end_minutes') % granularity_in_minutes()):
                raise QuantaBoundsException

            if check_date:
                if check_date != adefault.get('start_minutes'):
                    raise ConsecutiveDefaultsException

            check_date = adefault.get('end_minutes')

        # Delete old records
        old_defaults = db_sess.query(cls).filter_by(calendar_id=calendar_id).filter_by(dow=day_of_week).all()
        
        current_modification_time = False
        if old_defaults:
            # add a check to see if data being passed in is older than what is in the database
            current_modification_time = int(time.mktime(old_defaults[0].modification_date.timetuple()))

        if current_modification_time and last_modified and last_modified < current_modification_time:
            raise StaleDefaultsException

        for default in old_defaults:
            db_sess.delete(default)

        db_sess.commit()

        # Insert new records
        db_sess.begin_nested()
        for new_available_default in new_available_defaults:
            # JS gives a "work_units" which is in hours

            # Silently skip any zero size periods
            if new_available_default.get('start_minutes') == new_available_default.get('end_minutes'):
                continue

            minutes = new_available_default.get('work_units') * 60
            work_units_in_quanta = int(minutes / granularity_in_minutes())

            ad = AvailableDefaults() 
            ad.calendar_id = calendar_id
            ad.dow = day_of_week
            ad.start_minutes = new_available_default.get('start_minutes')
            ad.end_minutes = new_available_default.get('end_minutes')
            ad.work_units_in_quanta = work_units_in_quanta
            ad.comments = new_available_default.get('comments')
            db_sess.save(ad)
        db_sess.commit()


    def _get_app_items(self):

        return {u'start_minutes'  : self.start_minutes,
                u'end_minutes'    : self.end_minutes,
                u'work_units_in_quanta'     : self.work_units_in_quanta,
                u'comments'       : self.comments or u''}


    def match_period(self,period):
        if 'exception_date' in period:
            del period['exception_date']
        return period.items() == self._get_app_items().items()

    def js_dow(self):
        """python date weekday format is 0 = monday, 6 = sunday
           js date is 0 = sunday, 6 = saturday""" 
        # Handle the rollover of sunday from six back to zero
        if self.dow == 6:
            return 0
        else:
            return self.dow + 1
 
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
            if k == ('work_units_in_quanta'):
                # Convert to hours for the UI
                output['work_units'] = self.work_units_in_quanta / 2.0
                continue
            if k == ('dow'):
                output[k] = self.js_dow()
                continue
            output[k] = self.__dict__[k]
            
        return output 

