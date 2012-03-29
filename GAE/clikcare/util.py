# -*- coding: utf-8 -*-

from datetime import date, timedelta
import logging
from babel.dates import format_date, format_datetime


# key, value
def getAllRegions():
    return [('mtl-downtown', _(u'Montreal - Downtown').decode("UTF-8")),
            ('mtl-westisland', _(u'Montreal - West-Island').decode("UTF-8"))
            ]
    
# key, value
def getAllCategories():
    return [(u"physiotherapy", _(u"Physiotherapist").decode("UTF-8")),
            (u"chiropractor", _(u"Chiropractor").decode("UTF-8")),
            (u"osteopath", _(u"Osteopath").decode("UTF-8"))
        ]

# key, value
def getAllSpecialities():
    return [("cardiology", _(u"Cardiology").decode("UTF-8")),
            ("pneumology", _(u"Pneumology").decode("UTF-8")),
            ("orthopedic", _(u"Orthopedic").decode("UTF-8")),
            ("sports", _(u"Sports").decode("UTF-8")),
            ("neurology", _(u"Neurology").decode("UTF-8")),
            ("pediatric", _(u"Pediatric").decode("UTF-8")),
            ("geriatric", _(u"Geriatric").decode("UTF-8"))
        ]

def getAllSchools():
    return [("concordia", _(u"Concordia University").decode("UTF-8")),
            ("mcgill", _(u"McGill University").decode("UTF-8")),
            ("udem", _(u"Université de Montréal").decode("UTF-8")),
            ("uqtr", _(u"Université de Québec à Trois-Rivières").decode("UTF-8")),
            ("usherb", _(u"Université de Sherbrooke").decode("UTF-8"))
        ]

def getAllDiplomas():
    return [("bachelors", _(u"Bachelor's").decode("UTF-8")),
            ("masters", _(u"Master's").decode("UTF-8")),
            ("phd", _(u"Ph.D").decode("UTF-8"))
        ]


def getDatesList():
    ''' Return a list of date from tomorrow to 3 weeks from now'''
    datesList = []
    d = date.today()
    logging.info(d)
    oneDay = timedelta(days=1)
    for n in range(21):
        d = d + oneDay
        dateTuple = (unicode(d), formatDateFR(d))
        datesList.append(dateTuple)
    return datesList

def getTimesList():
    startTimeList = range(7, 22)
    timeStringList = map(lambda x: (unicode(x), formatTimeFR(x)), startTimeList)
    return timeStringList

def formatDateFR(date):
    return format_date(date, u"d MMMM yyyy (EEEE)", locale='fr')

def formatTimeFR(startTime):
    return unicode(startTime) + 'h - ' + str(startTime + 1) + 'h'

# is this method used anywhere?
def formatDateTimeNoSeconds(datetime):
    return format_datetime(datetime, u"d MMMM yyyy (EEEE) H:m", locale='en')

