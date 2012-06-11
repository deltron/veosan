

import logging
from google.appengine.ext import ndb
from data.model import Booking, Provider, Schedule
from datetime import time, date, datetime, timedelta

###
### Timeslots available in a day
###

def create_time_tuple(start, end):
    return (time(start), time(end))

def create_one_hour_timeslot(start):
    return create_time_tuple(start, start+1)

timeslots = map(create_one_hour_timeslot, range(8, 17))


def main_search(booking):
    # perfect match
    providers = find_providers_perfect_match(booking)
    logging.info('perfect match found %s available providers' % len(providers))
    if (len(providers) == 0):
        # if no providers found expand hours to before and after
        logging.info('No perfect match providers found, expanding search to other time on same day')
        providers = find_providers_alternate_time(booking)
        # imperfect match (other days)
    
        # imperfect match (other locations)
    return providers

    
def timeslot_distance(ts1, ts2):
    time_diff = datetime.combine(date.today(), ts1[0]) - datetime.combine(date.today(), ts2[0])
    return abs(time_diff.total_seconds())


def filter_providers_same_day_alternate_time(booking, providerQuery):
    providers = []
    request_day = booking.requestDateTime.weekday()
    request_start = booking.requestDateTime.hour
    request_end = request_start + 1 # Hack: appointments last one hour
    request_timeslot = (time(request_start), time(request_end))
    
    # sort timeslots based on distance to reuqest timeslot
    sorted_timeslots = sorted(timeslots, key=lambda t: timeslot_distance(t, request_timeslot))
    logging.info('sorted timeslots %s' % sorted_timeslots)
    
    
    return providers
    
    

def filter_providers_based_on_schedule(booking, providerQuery):
    providers = []
    # unpack booking
    request_day = booking.requestDateTime.weekday()
    request_start = booking.requestDateTime.hour
    request_end = request_start + 1 # Hack: appointments last one hour
    # eliminate providers based on schedule and previous bookings
    for p in providerQuery:
        scheduleQuery = Schedule.query(Schedule.provider==p.key, Schedule.day==request_day)
        #scheduleQuery = ndb.gql('''Select * from Schedule WHERE provider = :1 AND day = :2''', p.key, request_day)
        schedulesCount = scheduleQuery.count(limit=48) # putting this here so we never forget the limit (when schedule expands to full calendar)
        if (schedulesCount > 0):
            for s in scheduleQuery:
                logging.info('Checking if schedule %s overlaps request %s-%s' % (s.repr(), request_start, request_end))
                # manually check if hours match (because of BadFilterError: "Only one property per query may have inequality filters")
                logging.info('%s >= %s & %s <= %s' % (request_start, s.startTime, request_end, s.endTime))
                if (request_start >= s.startTime) & (request_end <= s.endTime):
                    logging.info('Found schedule match for provider {0}, schedule {1}:'.format(p.key, s.repr()))
                    # check if provider does not have a previous appointment conflicting with this one
                    conflicting_booking = Booking.query(Booking.provider==p.key, Booking.dateTime==booking.requestDateTime).get()
                    if not conflicting_booking:
                        providers.append(p)
                    else:
                        logging.info('|- Conflicting booking at %s'.format(conflicting_booking.dateTime.strftime("%H:%M")))
                else:
                    logging.info('Schedule hours do not match {0}'.format(s.repr()))
        else:
            logging.info('No schedule match for provider {0} on day'.format(p, request_day))
    # return list of providers available
    return providers


def display_general_provider_universe_stats(booking):
    # unpack booking request
    requestCategory = booking.requestCategory
    requestLocation = booking.requestLocation
    # general debug stats
    providerUniverseCount = Provider.query().count()
    logging.info('Total provider universe: %s' % providerUniverseCount)
    broadMatchCount = Provider.query(Provider.category==requestCategory, Provider.location==requestLocation).count()
    logging.info('Found %s providers offering %s in %s (ignoring terms agreement)' % (broadMatchCount, requestCategory, requestLocation))
    
    
def find_providers_perfect_match(booking):
    '''
        Create list of best provider to match request
    '''
    # unpack booking request
    requestCategory = booking.requestCategory
    requestLocation = booking.requestLocation
    # match on location and category, sort by experience (ascending start_year)
    providers_wide_query = Provider.query(Provider.category==requestCategory, Provider.location==requestLocation, Provider.terms_agreement==True, Provider.enable==True).order(Provider.start_year)
    logging.info('Found %s providers offering %s in %s (with terms)' % (providers_wide_query.count(), requestCategory, requestLocation))
    providers = filter_providers_based_on_schedule(booking, providers_wide_query)
    logging.info('Found %s providers offering %s in %s at requested date and time' % (providers_wide_query.count(), requestCategory, requestLocation))
    return providers


def find_providers_alternate_time(booking):
    '''
        Create list of providers that are available on the same day, but at a different time
    '''
    # match on location and category, sort by experience (ascending start_year)
    providers_wide_query = Provider.query(Provider.category==booking.requestCategory, Provider.location==booking.requestLocation, Provider.terms_agreement==True, Provider.enable==True).order(Provider.start_year)
    logging.info('Found %s providers offering %s in %s (with terms)' % (providers_wide_query.count(), booking.requestCategory, booking.requestLocation))
    providers = filter_providers_same_day_alternate_time(booking, providers_wide_query)
    logging.info('Found %s providers offering %s in %s at requested date but alternate time' % (providers_wide_query.count(), booking.requestCategory, booking.requestLocation))
    return providers
    


def findBestProviderForBookingRequest(booking):
    '''
        OLD method returns single provider
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
