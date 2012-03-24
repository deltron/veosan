# -*- coding: utf-8 -*-
from datetime import date, timedelta
import logging
from babel.dates import format_date
import gettext

# key, value
def getAllRegions():
    t = gettext.translation('clikcare', 'locale', languages=['fr'], fallback=False)
    _ = t.ugettext
    return [('mtl-downtown', _('Montreal - Downtown')),
            ('mtl-westisland', _('Montreal - West-Island'))  #'Montreal - Ouest de l''ile
            ]
    
# key, value
def getAllCategories():
    return [("physiotherapy", "Physiotherapeute"),
            ("chiropractor", "Chiropracticien"),
            ("osteopath", "Osteopathe")
        ]

# key, value
def getAllSpecialities():
    return [("cardiology", "Cardiologie"),
            ("pneumology", "Pneumologie"),
            ("orthopedic", "Orthopédie"),
            ("sports", "Sportive"),
            ("neurology", "Neurologie"),
            ("pediatric", "Pédiatrie"),
            ("geriatric", "Gériatrie")
        ]

def getAllSchools():
    return [("concordia", "Concordia University"),
            ("mcgill", "McGill University"),
            ("udem", "Universit&eacute; de Montr&eacute;al"),
            ("uqtr", "Universit&eacute; de Qu&ebec &agrave; Trois-Rivieres"),
            ("usherb", "Universit&eacute; de Sherbrooke")
        ]

def getAllDiplomas():
    return [("bachelors", "Baccalaureat"),
            ("masters", "Maitrise"),
            ("doctor", "Doctorat")
        ]


def getDatesList():
    ''' Return a list of date from tomorrow to 3 weeks from now'''
    datesList = []
    d = date.today()
    logging.info(d)
    oneDay = timedelta(days=1)
    for n in range(21):
        d = d + oneDay
        dateTuple = (str(d), formatDateFR(d))
        datesList.append(dateTuple)
    return datesList

def getTimesList():
    startTimeList = range(7,22)
    timeStringList = map(lambda x: (str(x), formatTimeFR(x)), startTimeList)
    return timeStringList

def formatDateFR(date):
    return format_date(date, "d MMMM yyyy (EEEE)", locale='fr')

def formatTimeFR(startTime):
    return str(startTime) + 'h - ' + str(startTime+1) + 'h'
