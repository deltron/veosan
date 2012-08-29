#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import calendar
from datetime import date, timedelta
import logging
from datetime import time, date, datetime, timedelta
from collections import namedtuple
from functools import partial
from webapp2_extras.i18n import format_date, format_datetime
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.i18n import to_utc

###
### TimeSlots and DatetimeSlot
###

# Timeslot represents a period on the calendar using two datetimes
Timeslot = namedtuple('Timeslot', "start end")


def create_one_hour_timeslot(datetime_start):
    datetime_end = datetime.combine(datetime_start.date(), time(datetime_start.time().hour + 1, datetime_start.time().minute))
    return Timeslot(datetime_start, datetime_end)
    
def create_one_hour_timeslot_on_date(date, start):
    return Timeslot(datetime.combine(date, time(start)), datetime.combine(date, time(start + 1)))

def create_one_hour_timeslots_over_range(date, start_hour, end_hour):
    return map(partial(create_one_hour_timeslot_on_date, date), range(start_hour, end_hour))

def timeslot_distance(ts1, ts2):
    ''' helper method for sorting '''
    time_diff = ts1.start - ts2.start
    return abs(time_diff.total_seconds())

###
### Date and Time Lists
###

def getDatesList():
    ''' Return a list of date from tomorrow to 3 weeks from now'''
    datesList = []
    d = date.today()
    #logging.info(d)
    oneDay = timedelta(days=1)
    for n in range(21):
        d = d + oneDay
        dateTuple = (unicode(d), format_date_weekday_after(d))
        datesList.append(dateTuple)
    return datesList

def get_time_list():
    time_list = []
    for t in range(7, 23):
        time_list.append((t, format_hour(t)))
    
    return time_list

def getScheduleTimeslots():
    # returns a list of list(name, start time, end time)
    return ((_(u"Morning"), '8', '12'),
             (_(u"Afternoon"), '12', '18'),
             (_(u"Evening"), '18', '21')
            )

def get_days_of_the_week():
    return [ ('monday', _('Monday')),
             ('tuesday', _('Tuesday')),
             ('wednesday', _('Wednesday')),
             ('thursday', _('Thursday')),
             ('friday', _('Friday')),
             ('saturday', _('Saturday')),
             ('sunday', _('Sunday')),
           ]

def get_day_of_the_week_from_python_weekday(weekday_index):
    return get_days_of_the_week()[weekday_index]

def tomorrow():
    d = date.today()
    oneDay = timedelta(days=1)
    return d + oneDay


###
###  Date and Time Formating
###

def format_date_weekday_after(date):
    return format_date(date, u"d MMMM yyyy (EEEE)")

def format_datetime_with_weekday(datetime):
    if datetime:
        lang = _('en')
        if (lang == 'fr'):
            return "%s %s %s" % (format_datetime(datetime, "EEEE 'le' d MMMM yyyy"), _(u"at"), format_datetime(datetime, "H:mm"))
        else:
            return "%s %s %s" % (format_datetime(datetime, "EEEE MMMM d, yyyy"), _(u"at"), format_datetime(datetime, "H:mm a"))
    else:
        return ""

def format_date_with_weekday(date):
    lang = _('en')
    if (lang == 'fr'):
        return format_date(date, "EEEE 'le' d MMMM yyyy")
    else:
        return format_date(date, "EEEE MMMM d, yyyy")

def format_datetime_full(datetime):
    lang = _('en')
    if (lang == 'fr'):
        return "%s %s %s" % (format_datetime(datetime, "EEEE 'le' d MMMM yyyy"), _(u"at"), format_datetime(datetime, "H:mm"))
    else:
        return "%s %s %s" % (format_datetime(datetime, "EEEE d MMMM yyyy"), _(u"at"), format_datetime(datetime, "H:mm a"))
        
# delete this? not locale or time-zone aware
def format_hour(hour):
    lang = _('en')
    if hour:
        # take a number in 24-hour format and return 13h or 1 PM
        if (lang == 'fr'):
            return u'%sh' % hour
        else :
            AMPM = u'AM'
            hour_en = hour
            if (int(hour) == 12):
                hour_en = hour
                AMPM = u'PM'
            elif (int(hour) > 12):
                hour_en = int(hour) - 12
                AMPM = u'PM'
            return u'%s %s' % (hour_en, AMPM)
    else:
        return ""

def formatTimeToOneHourPeriod(startTime):
    lang = _('en')
    endTime = startTime + 1
    if (lang == 'fr'):
        return unicode(startTime) + u'h - ' + unicode(endTime) + u'h'
    else:
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

def format_datetime_noseconds(datetime):
    if datetime:
        return format_datetime(datetime, "yyyy-MM-dd H:mm")
    else:
        ""

def format_datetime_booking_form(datetime):
    return format_datetime(datetime, "yyyy-MM-dd H:mm:ss", rebase=False)

def format_weekday(date):
    return format_date(date, 'EEEE')

def format_date_medium(date):
    return format_date(date, format="medium")

def format_datetime_hour_min(datetime):
    lang = _('en')
    if (lang == 'fr'):
        return "%s" % format_datetime(datetime, "H:mm", rebase=False)
    else:
        return "%s" % format_datetime(datetime, "H:mm a", rebase=False)
    return 

def format_datetime_withseconds_convert_east_tz(datetime):
    return format_datetime(datetime, "yyyy-MM-dd H:mm:ss", rebase=True)


def string_to_datetime(string_date):
    return to_utc(datetime.strptime(string_date, "%Y-%m-%d"))

def string_to_time(string_time):
    return to_utc(datetime.strptime(str(string_time), "%H"))

