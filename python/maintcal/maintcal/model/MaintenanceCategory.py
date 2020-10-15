from maintcal.model.MaintcalModel import MaintcalModel

class MaintenanceCategory(MaintcalModel):
    def __init__(self, name=u'', description=u''):
        self.name = name
        self.description = description
    
    def __str__(self):
        return self.name
    
    def __int__(self):
        return self.id
