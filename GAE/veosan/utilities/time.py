#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from datetime import time, date, datetime, timedelta
from collections import namedtuple
from functools import partial
from webapp2_extras.i18n import format_date, format_datetime, format_time, format_currency
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
        time_obj = string_to_time(str(t))
        time_list.append((t, format_time(time_obj, format="short", rebase=True)))
    
    return time_list

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

def format_datetime_full(datetime):
    lang = _('en')
    if (lang == 'fr'):
        return "%s %s %s" % (format_datetime(datetime, "EEEE 'le' d MMMM yyyy"), _(u"at"), format_datetime(datetime, "H:mm"))
    else:
        return "%s %s %s" % (format_datetime(datetime, "EEEE d MMMM yyyy"), _(u"at"), format_datetime(datetime, "H:mm a"))
        
def format_datetime_noseconds(datetime):
    if datetime:
        return format_datetime(datetime, "yyyy-MM-dd H:mm")
    else:
        ""
        
def format_datetime_booking_form(datetime):
    return format_datetime(datetime, "yyyy-MM-dd H:mm:ss", rebase=False)

def format_weekday(date):
    return format_date(date, 'EEEE')

def format_datetime_withseconds_convert_east_tz(datetime):
    return format_datetime(datetime, "yyyy-MM-dd H:mm:ss", rebase=True)

def string_to_datetime(string_date):
    return to_utc(datetime.strptime(string_date, "%Y-%m-%d"))

def string_to_time(string_time):
    if string_time:
        if isinstance( string_time, int ):
            parse_format = "%H"
        elif string_time.find(':') != -1:
            parse_format = "%H:%M"
        else:
            parse_format = "%H"
    else:
        return None
    return to_utc(datetime.strptime(str(string_time), parse_format))


def human_readable_date_decay(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"



# format currency
def string_to_currency(string_currency):
    return format_currency(string_currency, "$")


