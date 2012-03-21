
import dateutil.relativedelta as R
import dateutil.parser as P
from datetime import date, timedelta

def getAllRegions():
    return ['Montreal - Centre-Ville',
            'Montreal - Ouest de l''ile']
    
def getAllSpecialties():
    return ["Physiotherapeute",
             "Orthotherapeute",
             "Chiropracticien",
             "Osteopathe"]
    

def getDatesList():
    datesList = []
    d = date.today()
    oneDay = timedelta(days=1)
    for n in range(21):
        d = d + oneDay
        datesList.append(d)
    return datesList
        