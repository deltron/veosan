import logging
from data.model import Provider, Schedule, Booking
from datetime import datetime, time
from utilities.time import create_one_hour_timeslots_over_range, create_one_hour_timeslot, timeslot_distance, get_days_of_the_week


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
        return (self.provider.location == request.request_location) & (self.timeslot.start == request.request_datetime)
 
    def is_perfect_timeslot_match(self, request):
        return self.timeslot.start == request.request_datetime

    def is_perfect_location_match(self, request):
        return self.provider.location == request.request_location
      

def provider_search(booking):
    '''
        1. Select the closest available timeslot per provider
        2. Sorts all booking responses by proximity to requested time
        
        Returns list of BookingResponse
    '''
    display_general_provider_universe_stats(booking)
    # unpack booking request
    request_category = booking.request_category
    #request_location = booking.request_location
    # match on location and category, sort by experience (ascending start_year)
    providers_wide_query = Provider.query(Provider.category==request_category).order(Provider.start_year, Provider.created_on)
    #if booking.request_homecare:
    #    providers_wide_query = providers_wide_query.filter(Provider.practice_sites=='onsite')
    logging.info('Found %s providers offering %s (enabled and with terms)' % (providers_wide_query.count(), request_category))
    # sort by best available timeslot and filter out booking conflicts
    booking_responses = filter_and_sort_providers_based_on_schedule(booking, providers_wide_query)
    logging.info('Returning %s booking-responses offering %s at requested date and time' % (len(booking_responses), request_category))
    return booking_responses


def display_general_provider_universe_stats(booking):
    # unpack booking request
    request_category = booking.request_category
    
    # ignore location for now
    #request_location = booking.request_location
    
    # general debug stats
    providerUniverseCount = Provider.query().count()
    logging.info('Total provider universe: %s' % providerUniverseCount)
    broadMatchCount = Provider.query(Provider.category==request_category).count()
    logging.info('Found %s providers offering %s (ignoring enable and terms agreement)' % (broadMatchCount, request_category))


def filter_and_sort_providers_based_on_schedule(booking, providerQuery):
    '''
        Loops over the providers and find the best available timeslot for each of them
        Sorts the list by ascending proximity to the requested time
    '''
    booking_responses = []
    request_timeslot = create_one_hour_timeslot(booking.request_datetime)
    #logging.info('request timeslot: %s %s' % request_timeslot)
    for p in providerQuery:
        # list all available timeslots in order of proximity to requested datetime
        sorted_available_timeslots = get_sorted_schedule_timeslots(p, request_timeslot)
        # remove existing bookings
        sorted_available_timeslots_without_conflicts = filter_out_timeslots_with_existing_bookings(sorted_available_timeslots, p, request_timeslot)
        if sorted_available_timeslots_without_conflicts: # not empty
            best_ts = sorted_available_timeslots_without_conflicts[0]
            br = BookingResponse(p, best_ts)
            booking_responses.append(br)
    # sort all responses by distance to the request
    sorted_responses = sorted(booking_responses, key=lambda br: timeslot_distance(br.timeslot, request_timeslot))
    # limit to 3 results
    returned_responses = sorted_responses[0:3]
    # ..and return
    return returned_responses


def filter_out_timeslots_with_existing_bookings(available_timeslots, provider, request_timeslot):
    '''
        Remove provider's booking from the list of available timeslots for the day of the request
    '''
    day_start = datetime.combine(request_timeslot.start.date(), time(0, 0, 0))
    day_end = datetime.combine(request_timeslot.start.date(), time(23, 59, 59))
    #  
    request_day_confirmed_bookings = Booking.query(Booking.provider==provider.key, Booking.datetime > day_start, Booking.datetime < day_end).fetch()
    logging.debug('bookings for today: %s' % request_day_confirmed_bookings)
    # Hack, bookings are considered to be 1 hour long 
    # TODO Add end_datetime in Booking to generalize this
    booking_datetimes = map(lambda b: b.datetime, request_day_confirmed_bookings)
    booking_timeslots = map(create_one_hour_timeslot, booking_datetimes)
    logging.debug("booking timeslots: %s" % booking_timeslots)
    # filter out previous booking engagements
    logging.debug("available_timeslots: %s" % available_timeslots)
    available_timeslots_without_conflicts = filter(lambda a: a not in booking_timeslots, available_timeslots)
    logging.debug("conflicts removed: %s" % available_timeslots_without_conflicts)
    return available_timeslots_without_conflicts
       
       
    
def get_sorted_schedule_timeslots(provider, request_timeslot):
    '''
        Get a provider's timeslots ordered by proximity to the requested time
        This method is limited to the day of the request for now. Eventually expand to multi-day search
    '''
    
    # returns day of week (0=monday, 1=tuesday, etc.)
    request_day = request_timeslot.start.weekday()
    
    # map the number to the actual day
    request_day_key = get_days_of_the_week()[request_day][0]
    
    request_date = request_timeslot.start.date()
    scheduleQuery = Schedule.query(Schedule.provider==provider.key, Schedule.day==request_day_key)
    timeslots = []
    for s in scheduleQuery:
        ts = create_one_hour_timeslots_over_range(request_date, s.start_time, s.end_time)
        timeslots = timeslots + ts
    # sort
    sorted_timeslots = sorted(timeslots, key=lambda t: timeslot_distance(t, request_timeslot))
    return sorted_timeslots

