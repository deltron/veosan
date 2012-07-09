import logging
# veo
import data.db as db
from utilities import time
from base import BaseHandler
from data.model import Schedule
from handler.auth import provider_required

class ProviderBaseHandler(BaseHandler):       
    def render_schedule(self, provider, availableIds, **kw):
        timeslots = time.getScheduleTimeslots()
        days = time.getWeekdays()
        timeslot_ids = map(lambda x: "%s-%s-%s" % (x[0][0], x[1][1], x[1][2]),  [(d,ts) for d in days for ts in timeslots])
        logging.info("timeslot ids %s" % timeslot_ids)
        skipped_available_ids = [a for a in availableIds if a not in timeslot_ids]
        logging.info("skipped available ids %s" % skipped_available_ids)
        self.render_template('provider/schedule.html', provider=provider, availableIds=availableIds, timeslots=timeslots, days=days, skipped_available_ids=skipped_available_ids, **kw)
    
    @staticmethod
    def render_bookings(handler, provider, **kw):
        bookings = provider.get_future_bookings()
        logging.info('Bookings:' + str(bookings))
        handler.render_template('provider/bookings.html', provider=provider, bookings=bookings, **kw)

    def render_public_profile(self, provider, **kw):
        self.render_template('provider/public_profile.html', provider=provider, **kw)


class ProviderScheduleHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        availableIds = provider.getAvailableScheduleIds()
        logging.info('available ids' + str(availableIds))
        self.render_schedule(provider, availableIds)
           
    @provider_required
    def post(self):
        logging.debug('ProviderScheduleHandler POST')
        urlsafe_key = self.request.get('key')
        day_time = self.request.get('day_time')
        day, startTime, endTime = day_time.split('-')
        operation = self.request.get('operation')
        logging.info("SAVE SCHEDULE: " + urlsafe_key + " " + day + "-" + startTime + "-" + endTime + " " + operation)
        
        provider = db.get_from_urlsafe_key(urlsafe_key)
        if (operation == 'add'):
            s = Schedule()
            s.provider = provider.key
            s.day = int(day)
            s.startTime = int(startTime)
            s.endTime = int(endTime)
            new_schedule_key = s.put()
            logging.info('New Schedule saved: %s' % new_schedule_key)
        elif (operation == 'remove'):
            schedule_to_delete = Schedule.query(Schedule.provider == provider.key, Schedule.day == int(day), Schedule.startTime == int(startTime)).get()
            logging.info('deleting schedule' + str(schedule_to_delete))
            if (schedule_to_delete):
                schedule_to_delete.key.delete()
            else:
                logging.error("Can't find schedule to delete")  
        else:
            logging.info('Wrong operation save schedule:' + operation)

class ProviderBookingsHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        
        self.render_bookings(self, provider)


class ProviderPublicProfileHandler(ProviderBaseHandler):
    
    def get(self, vanity_url=None):
        # convert to lowercase
        vanity_url = vanity_url.lower()
        
        logging.info('(ProviderPublicProfileHandler.get) Received vanity_url: %s' % vanity_url)
        provider = db.get_provider_from_vanity_url(vanity_url)
        if provider:
            logging.info('(ProviderPublicProfileHandler.get) Found provider %s, rendering profile' % provider.email)

            # found a provider, render profile
            self.render_public_profile(provider)
        else:
            logging.info('(ProviderPublicProfileHandler.get) No provider found, sending to index')

            # nobody found, send them to the homepage
            self.redirect("/")