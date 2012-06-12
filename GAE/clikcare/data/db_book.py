import logging
from google.appengine.ext import ndb
from data.model import Booking, Provider, Schedule
from datetime import time, date, datetime, timedelta
from collections import namedtuple
from functools import partial

###
### TimeSlots and DatetimeSlot
###

# 2 datetimes: start and end on the same day
Timeslot = namedtuple('Timeslot', "start end")

#def create_time_slot(start, end):
#    return Timeslot(start, end)

def create_one_hour_timeslot(date, start):
    return Timeslot( datetime.combine(date, time(start)), datetime.combine(date, time(start+1)))

def create_timeslots_over_range(date, start_hour, end_hour):
    return map(partial(create_one_hour_timeslot, date), range(start_hour, end_hour))

def timeslot_distance(ts1, ts2):
    ''' helper method for sorting '''
    time_diff = ts1.start - ts2.start
    return abs(time_diff.total_seconds())

# All the time slots on a single days
#timeslots = create_timeslots_over_range(8, 17)


class BookingResponse():
    '''
        Class representing a possible booking availability
    '''
    provider = None
    timeslot = None
    
    def __init__(self, provider, ts):
        self.provider = provider
        self.timeslot = ts
        
    def is_perfect_match(self, request):
        return (self.provider.location == request.requestLocation) & (self.timeslot.start == request.requestDateTime)
 
    def is_perfect_timeslot_match(self, request):
        return self.timeslot.start == request.requestDateTime
    

def main_search(booking):
    '''
        1. Try perfect match of location and datetime 
        2. Look for other timeslots on the request day around the desired time
        
        Returns list of BookingResponse
    '''
    display_general_provider_universe_stats(booking)
    # unpack booking request
    requestCategory = booking.requestCategory
    requestLocation = booking.requestLocation
    # match on location and category, sort by experience (ascending start_year)
    providers_wide_query = Provider.query(Provider.category==requestCategory, Provider.location==requestLocation, Provider.terms_agreement==True).order(Provider.start_year)
    logging.info('Found %s providers offering %s in %s (with terms)' % (providers_wide_query.count(), requestCategory, requestLocation))
    # sort by best available timeslot and filter out booking conflicts
    booking_responses = filter_and_sort_providers_based_on_schedule(booking, providers_wide_query)
    logging.info('Found %s providers offering %s in %s at requested date and time' % (providers_wide_query.count(), requestCategory, requestLocation))
    return booking_responses


def display_general_provider_universe_stats(booking):
    # unpack booking request
    requestCategory = booking.requestCategory
    requestLocation = booking.requestLocation
    # general debug stats
    providerUniverseCount = Provider.query().count()
    logging.info('Total provider universe: %s' % providerUniverseCount)
    broadMatchCount = Provider.query(Provider.category==requestCategory, Provider.location==requestLocation).count()
    logging.info('Found %s providers offering %s in %s (ignoring terms agreement)' % (broadMatchCount, requestCategory, requestLocation))


def filter_and_sort_providers_based_on_schedule(booking, providerQuery):
    '''
        Loops over the providers and find the best available timeslot for each of them
        Sorts the list by ascending proximity to the requested time
    '''
    booking_responses = []
    # unpack booking
    request_date = booking.requestDateTime.date()
    logging.info('request date: %s' % request_date)
    request_start = booking.requestDateTime.hour
    request_timeslot = create_one_hour_timeslot(booking.requestDateTime.date(), request_start)
    logging.info('request timeslot: %s %s' % request_timeslot)
    for p in providerQuery:
        sorted_available_timeslots = get_sorted_schedule_timeslots(p, request_timeslot)
        # TODO: Filter out booking conflicts
        if sorted_available_timeslots: # not empty
            best_ts = sorted_available_timeslots[0]
            br = BookingResponse(p, best_ts)
            booking_responses.append(br)
    # sort all responses by distance to the request
    sorted_responses = sorted(booking_responses, key=lambda br: timeslot_distance(br.timeslot, request_timeslot))
    # return
    return sorted_responses

    
def get_sorted_schedule_timeslots(provider, request_timeslot):
    '''
        Get a provider's timeslots ordered by proximity to the requested time
        This method is limited to the day of the request for now. Eventually expand to multi-day search
    '''
    request_day = request_timeslot.start.weekday()
    request_date = request_timeslot.start.date()
    scheduleQuery = Schedule.query(Schedule.provider==provider.key, Schedule.day==request_day)
    timeslots = []
    for s in scheduleQuery:
        ts = create_timeslots_over_range(request_date, s.startTime, s.endTime)
        timeslots = timeslots + ts
    # sort
    sorted_timeslots = sorted(timeslots, key=lambda t: timeslot_distance(t, request_timeslot))
    return sorted_timeslots



###
### JUNK
###
 
def findBestProviderForBookingRequest(booking):
    '''
        Depreacated
        method returns single provider
        Returns provider that best matches: requestCategory, location, dateTime
    '''
    requestCategory = booking.requestCategory
    requestLocation = booking.requestLocation
    logging.info("request date_time x:" + str(booking.requestDateTime))
    requestDay = booking.requestDateTime.weekday()
    requestStartTime = booking.requestDateTime.hour
    # Hack: appointments last one hour
    requestEndTime = requestStartTime + 1
    logging.info('Looking for {0} in {1} available on day:{2} from {3} to {4}'.format(requestCategory, requestLocation, requestDay, requestStartTime, requestEndTime))
    providers = []
    providerUniverseCount = Provider.query().count()
    logging.info('Total provider universe: %s' % providerUniverseCount)
    broadMatchCount = Provider.query(Provider.category==requestCategory, Provider.location==requestLocation).count()
    logging.info('Found %s providers offering %s in %s' % (broadMatchCount, requestCategory, requestLocation))
    providersQuery = Provider.query(Provider.category==requestCategory, Provider.location==requestLocation, Provider.terms_agreement==True, Provider.enable==True)
    #gdb.GqlQuery('''Select * from Provider WHERE requestCategory = :1 AND requestLocation = :2''', requestCategory, requestLocation)
    providerCount = providersQuery.count(limit=50)
    logging.info('Found {0} providers in requestCategory and requestLocation. Narrowing down list using schedule...'.format(providerCount))
    for p in providersQuery:
        scheduleQuery = ndb.gql('''Select * from Schedule WHERE provider = :1 AND day = :2''', p.key, requestDay)
        schedulesCount = scheduleQuery.count(limit=48)
        if (schedulesCount > 0):
            for s in scheduleQuery:
                # manually check if hours match (because of BadFilterError: "Only one property per query may have inequality filters")
                if (requestStartTime >= s.startTime & requestEndTime <= s.endTime):
                    logging.info('Found schedule match for provider {0}, schedule {1}:'.format(p, s.repr()))
                    # check if provider does not have a previous appointment conflicting with this one
                    conflicting_booking = Booking.query(Booking.provider==p.key, Booking.dateTime==booking.requestDateTime).get()
                    if not conflicting_booking:
                        providers.append(p)
                    else:
                        logging.info('|- Conflicting booking at %s'.format(conflicting_booking.dateTime.strftime("%H:%M")))
                else:
                    logging.info('Schedule hours do not match {0}'.format(s.repr()))
        else:
            logging.info('No schedule match for provider {0} on day'.format(p, requestDay))
    logging.info('providers:' + str(providers))
    #providers = providersQuery.fetch(limit=1)
    if (len(providers) > 0):
        # TODO use ordering clause or Round-robin to find the top provider when list is longer than 1, currently uses the first in the list
        bestProvider = providers[0]
        logging.info('Found Best Provider: ' + bestProvider.fullName())
        return bestProvider
    else:
        logging.info('No Provider Found')
        return None
