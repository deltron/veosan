#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import calendar
from datetime import date, timedelta
import logging
from webapp2_extras.i18n import format_date, format_datetime
from webapp2_extras.i18n import lazy_gettext as _

languages = ['fr', 'en']

# String used on many pages
saved_message = _(u'Your changes were saved.')
    
# key, value
def getAllRegions():
    return [('mtl-downtown', _(u'Montreal - Downtown')),
            ('mtl-westisland', _(u'Montreal - West-Island'))
            ]
    
# key, value
def getAllCategories():
    return [(u"physiotherapy", _(u"Physiotherapist")),
            (u"chiropractor", _(u"Chiropractor")),
            (u"osteopath", _(u"Osteopath"))
        ]

# key, value
def getAllSpecialities():
    return [("sports", _(u"Sports")),
            ("geriatric", _(u"Geriatric")),            
            ("cardiology", _(u"Cardiology")),
            ("pneumology", _(u"Pneumology")),
            ("orthopedic", _(u"Orthopedic")),
            ("neurology", _(u"Neurology")),
            ("pediatric", _(u"Pediatric"))
        ]
    
def getAllSpecialitiesForPatient():
    z = getAllSpecialities()
    z.extend([ 
            ("other", _(u"Other")),
            ("dontknow", _(u"Not sure or don't know")),
            ("noanswer", _(u"Prefer not to answer"))
        ])
    return z


def getAllSchools():
    return [("na", _(u"Not Applicable")),
            ("concordia", _(u"Concordia University")),
            ("mcgill", _(u"McGill University")),
            ("udem", _(u"Universite de Montreal")),
            ("uqtr", _(u"Universite de Quebec a Trois-Rivieres")),
            ("usherb", _(u"Universite de Sherbrooke"))
        ]

def getAllAssociations():
    return [("oppq", _(u"Ordre professionnel de la physiotherapie du Quebec (OPPQ)")),
            ("cpa", _(u"Canadian Physiotherapy Association (CPA)")),
            ("campt", _(u"Canadian Academy of Manipulative Physiotherapy (CAMPT)"))
        ]

def getAllCertifications():
    return [("mckenzie", _(u"McKenzie Method")),
            ("art", _(u"Active Release Therapy (ART)"))
        ]


def getAllInsurance():
    return [("private", _(u"Private insurance (ex: employer)")),
            ("public", _(u"Public insurance (ex: CSST, SAAQ)")),
            ("other", _(u"Other coverage")),
            ("dontknow", _(u"Not sure or don't know")),
            ("noanswer", _(u"Prefer not to answer"))
        ]
    
def getAllConfirmation():
    return [("email", _(u"Email")),
            ("telephone", _(u"Telephone")),
        ]


def getDatesList():
    ''' Return a list of date from tomorrow to 3 weeks from now'''
    datesList = []
    d = date.today()
    logging.info(d)
    oneDay = timedelta(days=1)
    for n in range(21):
        d = d + oneDay
        dateTuple = (unicode(d), format_date_weekday_after(d))
        datesList.append(dateTuple)
    return datesList

def getTimesList():
    # this doesn't work for am/pm in english
    startTimeList = range(8, 21)
    timeStringList = map(lambda x: (unicode(x), formatTimeToOneHourPeriod(x)), startTimeList)
    return timeStringList

def getScheduleTimeslots():
    # returns a list of list(name, start time, end time)
    return ( ( _(u"Morning"), '8', '13'),
             ( _(u"Afternoon"), '13', '18'),
             ( _(u"Evening"), '18', '21')
            )

def getWeekdays():
    cal = calendar.Calendar(0)
    weekdays_lower = [(day, calendar.day_name[day]) for day in cal.iterweekdays()]
    logging.info('Weekdays from cal: %s' % weekdays_lower)
    weekdays = map( lambda s: (s[0], s[1].capitalize()), weekdays_lower)
    logging.info('Weekdays: %s' % weekdays)
    return weekdays

def format_date_weekday_after(date):
    return format_date(date, u"d MMMM yyyy (EEEE)")

def format_datetime_full(datetime):
    return format_datetime(datetime, "EEEE d MMMM yyyy") + " " +  _(u"at") + " " + format_datetime(datetime, "H:mm")

def format_hour(hour):
    lang = _('en')
    if (hour):
        '''take a number in 24-hour format and return 13h or 1 PM'''
        if (lang == 'fr'):
            return hour + u'h'
        else :
            AMPM = u'AM'
            if (hour > 12):
                hour_en = hour - 12
                AMPM = u'PM'
            return unicode(hour_en) + u' ' + AMPM
    else:
        return ""

def formatTimeToOneHourPeriod(startTime):
    lang = _('en')
    endTime = startTime + 1
    if (lang == 'fr'):
        return unicode(startTime) + u'h - ' + unicode(endTime) + u'h'
    else:
        logging.info('starttime %s' % startTime)
        startAMPM = u'AM'
        if (startTime > 12):
            startTime = startTime - 12
            startAMPM = u'PM'
        endAMPM = u'AM'
        if (endTime > 12):
            endTime = endTime - 12
            endAMPM = u'PM'
        return unicode(startTime) + u' ' + startAMPM + u' - ' + unicode(endTime) + u' ' + endAMPM
    
def format_30min_period(startTime, startMinutes):
    return u'START - END [placeholder]'

# is this method used anywhere?
def formatDateTimeNoSeconds(datetime):
    return format_datetime(datetime, "yyyy-MM-dd H:mm")


''' dump properties '''
def dump(obj):  
    return vars(obj)
    # todo split at the comma (replace with <br>)
    

