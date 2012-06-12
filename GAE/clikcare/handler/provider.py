import logging
#clik
import data.db as db
import util
from base import BaseHandler
from data.model import Schedule
from handler.auth import provider_required

class ProviderBaseHandler(BaseHandler):       
    def render_schedule(self, provider, availableIds, **extra):
        timeslots = util.getScheduleTimeslots()
        days = util.getWeekdays()
        self.render_template('provider/schedule.html', provider=provider, availableIds=availableIds, timeslots=timeslots, days=days, **extra)
    
    @staticmethod
    def render_bookings(handler, provider, **extra):
        bookings = db.fetch_future_bookings(provider)   
        logging.info('Bookings:' + str(bookings))
        handler.render_template('provider/bookings.html', provider=provider, bookings=bookings, **extra)


class ProviderScheduleHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        availableIds = provider.getAvailableScheduleIds()
        logging.info('available ids' + str(availableIds))
        self.render_schedule(provider, availableIds)
           
    @provider_required
    def post(self):
        logging.info('ProviderScheduleHandler POST')
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
