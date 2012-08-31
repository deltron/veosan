import logging
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from datetime import datetime, date, timedelta
from operator import itemgetter, attrgetter

# veo
import data.db as db
from data.model import Schedule
from forms.provider import ProviderPhotoForm, ProviderScheduleForm
from base import BaseHandler
from handler.auth import provider_required
import util
from utilities import time
from forms.booking import EmailOnlyBookingForm
from data import search_index
from google.appengine.api import search

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
        book_now_form = EmailOnlyBookingForm()
        self.render_template('provider/public/public_profile.html', book_now_form=book_now_form, provider=provider, **kw)

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
            



class ProviderSearchHandler(ProviderBaseHandler):
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        search_text = self.request.POST['search']
        
        logging.info("Search text: %s " % search_text)

        options = search.QueryOptions(
                                      limit=20, # the number of results to return
                                      #returned_fields=['first_name', 'last_name', 'city'],
                                      #snippeted_fields=['bio'],
                                      )

        query = search.Query(query_string=search_text, options=options)
        index = search.Index(name=search_index._PROVIDERS_INDEX_NAME)

        try:
            results = index.search(query)
            provider_search_results = []
            for scored_document in results:
                # retrieve providers for search results
                provider_urlsafe_key = scored_document.doc_id
                provider = ndb.Key(urlsafe=provider_urlsafe_key).get()
                provider_search_results.append(provider)
                
        except search.Error:
            logging.exception('Search failed')


        self.render_template("provider/network.html", provider=provider, provider_search_results=provider_search_results)


# BOOKING AND SCHEDULE STUFF
# *************************************

class ProviderBookingsHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        if provider:
            self.render_bookings(self, provider)




        

