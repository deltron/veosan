import logging
from google.appengine.ext import blobstore
from datetime import timedelta
from operator import itemgetter

# veo
import data.db as db
from forms.provider import ProviderPhotoForm
from base import BaseHandler
from handler.auth import provider_required
import util
from utilities import time

class ProviderBaseHandler(BaseHandler): 

    def render_profile(self, provider, **kw):
        upload_url = blobstore.create_upload_url('/provider/profile/photo/%s' % provider.vanity_url)
        upload_form = ProviderPhotoForm().get_form(self.request.GET)
        self.render_template('provider/profile.html', provider=provider, upload_form=upload_form, upload_url=upload_url, **kw)    

    @staticmethod
    def render_bookings(handler, provider, **kw):
        bookings = provider.get_future_confirmed_bookings()
        logging.info('Future Confirmed Bookings:' + str(bookings))
        handler.render_template('provider/bookings.html', provider=provider, bookings=bookings, **kw)

    def render_public_profile(self, provider, **kw):
        self.render_template('provider/public/public_profile.html', provider=provider, **kw)

    def render_cv(self, provider, **kw):
        self.render_template('provider/cv.html', provider=provider, **kw)

    def render_address(self, provider, **kw):
        self.render_template('provider/address.html', provider=provider, **kw)





class ProviderPublicProfileHandler(ProviderBaseHandler):
    
    def get(self, vanity_url=None):
        # convert to lowercase
        vanity_url = vanity_url.lower()
        
        logging.info('(ProviderPublicProfileHandler.get) Received vanity_url: %s' % vanity_url)
        provider = db.get_provider_from_vanity_url(vanity_url)
        if provider:
            logging.info('(ProviderPublicProfileHandler.get) Found provider %s, rendering profile' % provider.email)
            
            # add some dates & times to display part of schedule on page
            start_date = time.tomorrow()
            period = timedelta(days=14)
            
            schedules = provider.get_schedules()
            schedule_datetimes_dict = util.generate_complete_datetimes_dict(schedules, start_date, period)
            confirmed_bookings = provider.get_future_confirmed_bookings()
            datetimes_map = util.remove_confirmed_bookings_from_schedule(schedule_datetimes_dict, confirmed_bookings)
            
            dtm = datetimes_map
            
            date_time_list = []
            
            # flatten the map and give first 5 results
            # TODO: sort
            count = 0
            for (day_key, day_times) in dtm.items():
                if count >= 5:
                    break

                for t in day_times:
                    date_time_list.append((day_key, day_times, t))
                    count += 1
                    if count >= 5:
                        break
            
            date_time_list = sorted(date_time_list, key=itemgetter(0, 2))
            
            # found a provider, render profile
            self.render_public_profile(provider=provider, date_time_list=date_time_list)
            
            # increment view count, store async
            # we don't really care if it doesn't work
            # old --> use event log instead
            provider.profile_views += 1
            provider.put_async()

            # log the event
            user = self.get_current_user()
            if user and user.key == provider.user:
                self.log_event(user=provider.user, msg="Public profile: self-view")
            else:
                self.log_event(user=provider.user, msg="Public profile: public view")
                
        else:            
            logging.info('(ProviderPublicProfileHandler.get) No provider found, sending to index')

            # nobody found, send them to the homepage
            self.redirect("/")
            




# BOOKING AND SCHEDULE STUFF
# *************************************

class ProviderBookingsHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        if provider:
            self.render_bookings(self, provider)


