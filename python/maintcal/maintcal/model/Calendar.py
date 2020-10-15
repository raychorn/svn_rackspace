from datetime import timedelta
from maintcal.model.MaintcalModel import MaintcalModel

class Calendar(MaintcalModel):
    CRITICAL_SITES = 60
    def __init__(self, name, description, ticket_queue=0, active=False):
        self.name = name
        self.description = description
        self.tckt_queue_id = ticket_queue
        self.active = active
        self.timezone = None
        self.new_ticket_queue_id = 0
        self.new_ticket_category_id = 0
        self.new_ticket_status_id = 0
        self.time_before_ticket_refresh = timedelta(0)
        self.refresh_ticket_assignment = False
        self.refresh_ticket_queue_id = 0
        self.refresh_category_id = 0
        self.refresh_status_id = 0
        self.hold_tentative_time = timedelta(0)
    
    def __str__(self):
        return self.name
