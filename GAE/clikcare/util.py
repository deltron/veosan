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
