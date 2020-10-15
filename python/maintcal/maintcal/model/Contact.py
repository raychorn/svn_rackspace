from maintcal.model.MaintcalModel import MaintcalModel

class Contact(MaintcalModel):
    
    def __init__(self, id):
        self.id = id
        self.username = ''
    
    def __str__(self):
        if self.username:
            return self.username
        else:
            return ''
    
    def __int__(self):
        return self.id
