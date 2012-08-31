from utilities import time
from handler.provider import ProviderBaseHandler
from forms.provider import ProviderScheduleForm
import util
from handler.auth import provider_required
from data import db
from google.appengine.ext import ndb
import logging
from data.model import Schedule


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

        
        