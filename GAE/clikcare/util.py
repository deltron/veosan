#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from datetime import date, timedelta
import logging
from babel.dates import format_date, format_datetime
from babel import Locale
from base import lang

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
            ("udem", _(u"Universite de Montreal").decode("UTF-8")),
            ("uqtr", _(u"Universite de Quebec a Trois-Rivieres").decode("UTF-8")),
            ("usherb", _(u"Universite de Sherbrooke").decode("UTF-8"))
        ]

def getAllDiplomas():
    return [("bachelors", _(u"Bachelor's").decode("UTF-8")),
            ("masters", _(u"Master's").decode("UTF-8")),
            ("phd", _(u"Ph.D").decode("UTF-8"))
        ]

def getAllInsurance():
    return [("private", _(u"Private insurance (ex: employer)").decode("UTF-8")),
            ("public", _(u"Public insurance (ex: CSST, SAAQ)").decode("UTF-8")),
            ("other", _(u"Other coverage").decode("UTF-8")),
            ("dontknow", _(u"Not sure or don't know").decode("UTF-8")),
            ("noanswer", _(u"Prefer not to answer").decode("UTF-8"))
        ]

def getDatesList():
    ''' Return a list of date from tomorrow to 3 weeks from now'''
    datesList = []
    d = date.today()
    logging.info(d)
    oneDay = timedelta(days=1)
    for n in range(21):
        d = d + oneDay
        dateTuple = (unicode(d), formatDate(d))
        datesList.append(dateTuple)
    return datesList

def getTimesList():
    # this doesn't work for am/pm in english
    startTimeList = range(7, 21)
    timeStringList = map(lambda x: (unicode(x), formatTimeToOneHourPeriod(x)), startTimeList)
    return timeStringList

def getWeekdays():
    locale = Locale(lang)
    weekdays = locale.days['format']['wide'].items()
    logging.info( str(weekdays) )
    return weekdays

def formatDate(date):
    return format_date(date, u"d MMMM yyyy (EEEE)", locale=lang)

def format_hour(hour):
    '''take a number in 24-hour format and return 13h or 1 PM'''
    if (lang == 'fr'):
        return hour + u'h'
    else :
        AMPM = u'AM'
        if (hour > 12):
            hour_en = hour - 12
            AMPM = u'PM'
        return unicode(hour_en) + u' ' + AMPM

def formatTimeToOneHourPeriod(startTime):
    endTime = startTime + 1
    if (lang == 'fr'):
        return unicode(startTime) + u'h - ' + unicode(endTime) + u'h'
    else:
        startAMPM = u'AM'
        if (startTime > 12):
            startTimeEN = startTime - 12
            startAMPM = u'PM'
        endAMPM = u'AM'
        if (endTime > 12):
            endTimeEN = endTime - 12
            endAMPM = u'PM'
        return unicode(startTimeEN) + u' ' + startAMPM + u' - ' + unicode(endTimeEN) + u' ' + endAMPM
    
def format_30min_period(startTime, startMinutes):
    return u'START - END [placeholder]'

# is this method used anywhere?
def formatDateTimeNoSeconds(datetime):
    return format_datetime(datetime, u"d MMMM yyyy (EEEE) H:m", locale=lang)


''' dump properties '''
def dump(obj):  
    return vars(obj)
    # todo split at the comma (replace with <br>)
