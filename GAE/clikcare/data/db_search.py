import logging
from data.model import Provider, Schedule
from utilities.time import create_one_hour_timeslots_over_range, create_one_hour_timeslot, timeslot_distance


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
    

def provider_search(booking):
    '''
        1. Select the closest available timeslot per provider
        2. Sorts all booking responses by proximity to requested time
        
        Returns list of BookingResponse
    '''
    display_general_provider_universe_stats(booking)
    # unpack booking request
    request_category = booking.request_category
    request_location = booking.request_location
    # match on location and category, sort by experience (ascending start_year)
    providers_wide_query = Provider.query(Provider.category==request_category, Provider.location==request_location, Provider.enable==True, Provider.terms_agreement==True).order(Provider.start_year)
    logging.info('Found %s providers offering %s in %s (enabled and with terms)' % (providers_wide_query.count(), request_category, request_location))
    # sort by best available timeslot and filter out booking conflicts
    booking_responses = filter_and_sort_providers_based_on_schedule(booking, providers_wide_query)
    logging.info('Returning %s booking-responses offering %s in %s at requested date and time' % (len(booking_responses), request_category, request_location))
    return booking_responses


def display_general_provider_universe_stats(booking):
    # unpack booking request
    request_category = booking.request_category
    request_location = booking.request_location
    # general debug stats
    providerUniverseCount = Provider.query().count()
    logging.info('Total provider universe: %s' % providerUniverseCount)
    broadMatchCount = Provider.query(Provider.category==request_category, Provider.location==request_location).count()
    logging.info('Found %s providers offering %s in %s (ignoring enable and terms agreement)' % (broadMatchCount, request_category, request_location))


def filter_and_sort_providers_based_on_schedule(booking, providerQuery):
    '''
        Loops over the providers and find the best available timeslot for each of them
        Sorts the list by ascending proximity to the requested time
    '''
    booking_responses = []
    # unpack booking
    request_date = booking.request_datetime.date()
    logging.info('request date: %s' % request_date)
    request_start = booking.request_datetime.hour
    request_timeslot = create_one_hour_timeslot(booking.request_datetime.date(), request_start)
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
        ts = create_one_hour_timeslots_over_range(request_date, s.startTime, s.endTime)
        timeslots = timeslots + ts
    # sort
    sorted_timeslots = sorted(timeslots, key=lambda t: timeslot_distance(t, request_timeslot))
    return sorted_timeslots

