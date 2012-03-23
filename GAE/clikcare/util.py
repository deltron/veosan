# -*- coding: utf-8 -*-
from datetime import date, timedelta
import logging
from babel.dates import format_date

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
    ''' Return a list of date from tomorrow to 3 weeks from now'''
    datesList = []
    d = date.today()
    logging.info(d)
    oneDay = timedelta(days=1)
    for n in range(21):
        d = d + oneDay
        dateTuple = (d, formatDateFR(d))
        datesList.append(dateTuple)
    return datesList

def getTimesList():
    startTimeList = range(7,22)
    timeStringList = map(lambda x: (x, formatTimeFR(x)), startTimeList)
    return timeStringList

def formatDateFR(date):
    return format_date(date, "d MMMM yyyy (EEEE)", locale='fr')

def formatTimeFR(startTime):
    return str(startTime) + 'h - ' + str(startTime+1) + 'h'
