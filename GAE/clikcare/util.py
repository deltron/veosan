
from datetime import date, timedelta

# key, value
def getAllRegions():
    return [('mtl-downtown', 'Montreal - Centre-Ville'),
            ('mtl-westisland', 'Montreal - Ouest de l''ile')
            ]
    
# key, value
def getAllCategories():
    return [("physiotherapy", "Physiotherapeute"),
            ("chiropractor", "Chiropracticien"),
            ("osteopath", "Osteopathe")
        ]
    

def getDatesList():
    datesList = []
    d = date.today()
    oneDay = timedelta(days=1)
    for n in range(21):
        d = d + oneDay
        datesList.append(d)
    return datesList
        