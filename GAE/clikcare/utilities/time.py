
from datetime import time, date, datetime, timedelta
from collections import namedtuple
from functools import partial
    
    
###
### TimeSlots and DatetimeSlot
###

# Timeslot represents a period on the calendar using two datetimes
Timeslot = namedtuple('Timeslot', "start end")

def create_one_hour_timeslot(date, start):
    return Timeslot( datetime.combine(date, time(start)), datetime.combine(date, time(start+1)))

def create_one_hour_timeslots_over_range(date, start_hour, end_hour):
    return map(partial(create_one_hour_timeslot, date), range(start_hour, end_hour))

def timeslot_distance(ts1, ts2):
    ''' helper method for sorting '''
    time_diff = ts1.start - ts2.start
    return abs(time_diff.total_seconds())