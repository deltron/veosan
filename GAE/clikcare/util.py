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
        dateTuple = (d, formatDate(d))
        datesList.append(dateTuple)
    return datesList

def formatTime(startTime):
    return str(startTime) + 'h - ' + str(startTime+1) + 'h'

def getTimesList():
    startTimeList = range(7,22)
    timeStringList = map(lambda x: (x, formatTime(x)), startTimeList)
    return timeStringList

def formatDate(date):
    return format_date(date, "EEEE, d MMM yyyy", locale='fr')