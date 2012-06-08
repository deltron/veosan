

import logging
from google.appengine.ext import ndb
from data.model import Booking, Provider



def find_providers_for_booking_request(booking):
    '''
        Create list of best provider to match request
    '''
    # match on all criterias
    perfectMatch = Provider.query(Provider.category==booking.requestCategory, Provider.location==region, Provider.terms_agreement==True)
    
    # if no providers found expand hours to before and after
    
    


def findBestProviderForBookingRequest(booking):
    '''
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
    providersQuery = Provider.query(Provider.category==requestCategory, Provider.location==requestLocation, Provider.terms_agreement==True)
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
