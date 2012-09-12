# -*- coding: utf-8 -*-

import logging
import data.db as db
import util
from handler.base import BaseHandler
from datetime import datetime, date, timedelta
from utilities import time
from collections import namedtuple
from webapp2_extras.i18n import gettext as _
from handler.booking_pkg.booking_base_handler import BookingBaseHandler

        


WeekNav = namedtuple('WeekNav', 'prev_week this_week next_week')

class BookFromPublicProfileDisplaySchedule(BookingBaseHandler):
    
    def calculate_start_date_and_week_navigation(self, start_date, period):
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            week_nav = WeekNav(start_date - period, start_date, start_date + period)
            if (start_date <= time.tomorrow()): # start_date too early
                start_date = time.tomorrow()
                week_nav = WeekNav(None, start_date, start_date + period)
            max_date = date.today() + timedelta(days=45)
            logging.info('max date %s' % max_date)
            if (start_date >= max_date):
                start_date = max_date
                week_nav = WeekNav(start_date - period, start_date, None)
        else:
            start_date = time.tomorrow()
            week_nav = WeekNav(None, start_date, start_date + period)
        # return 2 values: stat_date and week_nav
        return start_date, week_nav
            
    
    def get(self, vanity_url=None, start_date=None, bk=None):
        '''
            Display Booking Schedule
        '''
        # provoder already selection from public profile
        period = timedelta(days=7)
        provider = db.get_provider_from_vanity_url(vanity_url)
        start_date, week_nav = self.calculate_start_date_and_week_navigation(start_date, period)
        schedules = provider.get_schedules()
        #logging.info('SCHEDULES %s' % schedules.fetch())
        schedule_datetimes_dict = util.generate_complete_datetimes_dict(schedules, start_date, period)
        #logging.info( 'SCHEDULES DICT %s' % schedule_datetimes_dict)
        confirmed_bookings = provider.get_future_confirmed_bookings()
        available_datetimes_map = util.remove_confirmed_bookings_from_schedule(schedule_datetimes_dict, confirmed_bookings)
        self.render_template('provider/public/booking_schedule.html', provider=provider, dtm=available_datetimes_map, week_nav=week_nav) 
        


