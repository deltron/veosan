import logging
from google.appengine.ext import ndb
from google.appengine.ext import blobstore

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
        bookings = provider.get_future_bookings()
        logging.info('Bookings:' + str(bookings))
        handler.render_template('provider/bookings.html', provider=provider, bookings=bookings, **kw)

    def render_public_profile(self, provider, **kw):
        book_now_form = EmailOnlyBookingForm()
        self.render_template('provider/public_profile.html', book_now_form=book_now_form, provider=provider, **kw)

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
            
            # found a provider, render profile
            self.render_public_profile(provider)
            
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
                                      limit=20,  # the number of results to return
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



class ProviderScheduleHandler(ProviderBaseHandler): 
     
    def render_schedule(self, provider, schedule_form=None, **kw):
        sq = provider.get_schedules()
        schedules = sq.fetch()
        days = time.get_days_of_the_week()
        times = time.get_time_list()
        
        schedule_mapmap = util.create_schedule_map(schedules)
        if not schedule_form:
            schedule_form = ProviderScheduleForm().get_form()
        self.render_template('provider/schedule.html', provider=provider, schedules=schedule_mapmap, times=times, days=days, schedule_form=schedule_form, **kw)
        
    
    @provider_required
    def get(self, vanity_url=None, operation=None, key=None, day=None, start_time=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        kwargs = {}
        if key:
            schedule_key = ndb.Key(urlsafe=key)
            
        if operation == 'add':
            logging.info("(ProviderEducationHandler.get) Add schedule key=%s" % key)
            #new_schedule.end_time = new_schedule.start_time + 4
            schedule_form = ProviderScheduleForm().get_form()
            schedule_form.day.data = day
            schedule_form.start_time.data = int(start_time)
            
            
            end_time = int(start_time) + 4
            max_time = max([k[0] for k in time.get_time_list()])
            if end_time > max_time:
                end_time = max_time
            
            schedule_form.end_time.data = int(end_time)
            
            kwargs['schedule_form'] = schedule_form
            kwargs['add'] = 'add'
            self.render_schedule(provider, **kwargs)

            
        elif operation == 'delete':
            logging.info("(ProviderEducationHandler.get) Delete schedule key=%s" % key)    
            schedule_key.delete()        
            # log the event
            self.log_event(user=provider.user, msg="Schedule delete")
            
            self.redirect('/provider/schedule/%s' % provider.vanity_url)

        elif operation == 'edit':
            logging.info("(ProviderEducationHandler.get) Edit schedule key=%s" % key)
            # get the object
            obj = schedule_key.get()
            # populate the form
            kwargs['schedule_form'] = ProviderScheduleForm().get_form(obj=obj)
            kwargs['edit_key'] = key
            
            self.render_schedule(provider, **kwargs)
        
        else:
            self.render_schedule(provider, **kwargs)
           
    @provider_required
    def post(self, vanity_url=None, operation=None, key=None):
        logging.info('ProviderScheduleHandler POST')        
        # instantiate and fill the form
        schedule_form = ProviderScheduleForm().get_form(self.request.POST, obj=Schedule())
        provider = db.get_provider_from_vanity_url(vanity_url)
        error_messages = None
        
        if schedule_form.validate():
            # Store schedule
            if operation == 'add':
                new_schedule = Schedule()
                schedule_form.populate_obj(new_schedule)
                new_schedule.provider = provider.key
                new_schedule.put()
                # stored eduction
                logging.debug("(ProviderSchedule.post) New schedule %s " % new_schedule)
                
            elif operation == 'edit':
                schedule_key = ndb.Key(urlsafe=key)
        
                if schedule_key:
                    schedule = schedule_key.get()
                    schedule_form.populate_obj(schedule)
                    schedule.put()
                    # stored
                    logging.info("(ProviderEducationHandler.post) Stored schedule key=%s" % schedule.key)
                else:
                    logging.info("(ProviderEducationHandler.post) No schedule found for key %s" % key)

            else:
                logging.error('Operation Not handled %s' % operation)
                
            self.render_schedule(provider)

        else:
            error_messages = schedule_form.errors
            logging.info('Schedule form did not validate: %s' % error_messages)
            
            kwargs = {}
            kwargs['schedule_form'] = schedule_form
            kwargs['edit_key'] = key

            self.render_schedule(provider, **kwargs)

        
        
        

