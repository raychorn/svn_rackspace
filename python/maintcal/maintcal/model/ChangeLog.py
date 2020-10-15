from maintcal.model.MaintcalModel import MaintcalModel

class ChangeLog(MaintcalModel):
    def __init__(self, table_id, row_id, contact, field, old_value, new_value):
        self.table_id = table_id
        self.contact = contact
        self.row_id = row_id
        self.field = field
        self.old_value = old_value
        self.new_value = new_value

def ServiceTypeChangeLog(service_type_id, contact, field, old_value, new_value):
    return ChangeLog('t', service_type_id, contact, field, old_value, new_value)

def MaintenanceChangeLog(maintenance_id, contact, field, old_value, new_value):
    return ChangeLog('m', maintenance_id, contact, field, old_value, new_value)

def ServiceChangeLog(service_id, contact, field, old_value, new_value):
    return ChangeLog('s', service_id, contact, field, old_value, new_value)

#class ServiceTypeChangeLog(ChangeLog):
#    def __init__(self, service_type_id, contact, field, old_value, new_value):
#        ChangeLog.__init__(self, 't', service_type_id, contact, field, old_value, new_value)
#        
#class MaintenanceChangeLog(ChangeLog):
#    def __init__(self, maintenance_id, contact, field, old_value, new_value):
#        ChangeLog.__init__(self, 'm', maintenance_id, contact, field, old_value, new_value)
#    
#class ServiceChangeLog(ChangeLog):
#    def __init__(self, service_id, contact, field, old_value, new_value):
#        ChangeLog.__init__(self, 's', service_id, contact, field, old_value, new_value)
