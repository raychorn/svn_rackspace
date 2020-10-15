from maintcal.lib.times_available import granularity_in_minutes

class TimesAvailableQuery(object):
    """
        This class represents a query for finding available time for a service.
   
        The entire service must fall between start and end datetimes
    """

    def __init__(self, start_maintcal_datetime, end_maintcal_datetime, service_length_in_quanta):

        self.service_length_in_quanta = service_length_in_quanta

        #hours = service_length
        #svc_minutes = 60 * float(hours)
        #self.service_length_in_quanta = int(svc_minutes / granularity_in_minutes())

        self.start_maintcal_datetime = start_maintcal_datetime
        self.end_maintcal_datetime = end_maintcal_datetime
