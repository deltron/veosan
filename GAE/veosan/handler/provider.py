import logging
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from webapp2_extras.i18n import lazy_gettext as _

# veo
import data.db as db
from data.model import Schedule, Education, Experience, ContinuingEducation
from forms.provider import ProviderAddressForm, ProviderEducationForm, ProviderContinuingEducationForm, ProviderExperienceForm, ProviderProfileForm, ProviderPhotoForm
from base import BaseHandler
from handler.auth import provider_required
from util import saved_message
from utilities import time

class ProviderBaseHandler(BaseHandler): 

    def render_profile(self, provider, **kw):
        upload_url = blobstore.create_upload_url('/provider/profile/photo/%s' % provider.vanity_url)
        upload_form = ProviderPhotoForm().get_form(self.request.GET)
        
        self.render_template('provider/profile.html', provider=provider, upload_form=upload_form, upload_url=upload_url, **kw)    
          
    def render_schedule(self, provider, availableIds, **kw):
        timeslots = time.getScheduleTimeslots()
        days = time.getWeekdays()
        timeslot_ids = map(lambda x: "%s-%s-%s" % (x[0][0], x[1][1], x[1][2]), [(d, ts) for d in days for ts in timeslots])
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

    def render_cv(self, provider, **kw):
        self.render_template('provider/cv.html', provider=provider, **kw)

    def render_address(self, provider, **kw):
        self.render_template('provider/address.html', provider=provider, **kw)


class ProviderMessageHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None, msg_key=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        messages = { 'new' : _("Welcome to Veosan! Please get started by completing your profile."),
                     'reset' : _("Welcome back! Password has been reset."),
                    }
        
        profile_form = ProviderProfileForm().get_form(obj=provider)
        self.render_profile(provider, profile_form=profile_form, success_message=messages[msg_key])
        

class ProviderEditAddressHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        logging.info("provider dump before edit:" + str(vars(provider)))
        form = ProviderAddressForm().get_form(obj=provider)
        self.render_address(provider, address_form=form)

    @provider_required
    def post(self, vanity_url=None):
        form = ProviderAddressForm().get_form(self.request.POST)
        
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            provider_key = db.storeProvider(provider, self.request.POST, form)
            provider = provider_key.get()

            self.render_address(provider, address_form=form, success_message=saved_message)

            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Success")

        else:
            # show validation error
            provider = db.get_provider_from_vanity_url(vanity_url)
            self.render_address(provider, address_form=form)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Validation Error")



class ProviderEditProfileHandler(ProviderBaseHandler):

    @provider_required    
    def get(self, vanity_url=None):
        provider = None
        
        if vanity_url:
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            logging.debug("(ProviderEditProfileHandler.get) Edit profile for provider %s" % provider.email)
            
            profile_form = ProviderProfileForm().get_form(obj=provider)
            
            self.render_profile(provider, profile_form=profile_form)
    
    @provider_required    
    def post(self, vanity_url=None):
        form = ProviderProfileForm().get_form(self.request.POST)
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            provider_key = db.storeProvider(provider, self.request.POST, form=form)
            provider = provider_key.get()
            self.render_profile(provider, profile_form=form, success_message=saved_message)

            # log the event
            self.log_event(user=provider.user, msg="Edit Profile: Success")

        else:
            # show error
            provider = db.get_provider_from_vanity_url(vanity_url)
            self.render_profile(provider, profile_form=form)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit Profile: Validation Error")

class ProviderProfilePhotoUploadHandler(ProviderBaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    
    @provider_required
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        logging.info("(ProviderAddressUploadHandler.post) Found provider: %s" % provider.email)
        
        upload_form = ProviderPhotoForm().get_form(self.request.POST)
        upload_files = self.get_uploads(upload_form.profile_photo.name)[0]
        
        logging.info("(ProviderAddressUploadHandler.post) Uploaded blob key: %s " % upload_files.key())
        provider.profile_photo_blob_key = upload_files.key()
        provider.put()
        
        # redirect to profile page        
        self.redirect('/provider/profile/%s' % provider.vanity_url) 

        # log the event
        self.log_event(user=provider.user, msg="Edit Profile: Upload Photo")


class ProviderCVHandler(ProviderBaseHandler):
    forms = { 'education' : ProviderEducationForm,
              'experience' : ProviderExperienceForm,
              'continuing_education' : ProviderContinuingEducationForm,
            }

    objs = { 'education' : Education,
             'experience' : Experience,
             'continuing_education' : ContinuingEducation
            }

    def generate_blank_forms(self):
        kwargs = {}
        
        # create blank forms
        for key in self.forms:
            kwargs[key + '_form'] = self.forms[key]().get_form()

        return kwargs

    @provider_required
    def get(self, vanity_url=None, section=None, operation=None, key=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        kwargs = self.generate_blank_forms()
        section_key = None

        if key:
            section_key = ndb.Key(urlsafe=key)
        

        if section_key:
            if operation == 'delete':
                logging.info("(ProviderEducationHandler.get) Delete section %s key=%s" % (section, key))
                            
                section_key.delete()
                
                # success, empty forms so you can play again            
                kwargs = self.generate_blank_forms()
            
                # log the event
                self.log_event(user=provider.user, msg="Edit CV: %s %s success" % (operation, section))

            if operation == 'edit':
                logging.info("(ProviderEducationHandler.get) Edit section %s key=%s" % (section, key))
                
                # get the object
                obj = section_key.get()
                
                # populate the form
                kwargs[section + "_form"] = self.forms[section]().get_form(obj=obj)
                kwargs['edit'] = section
                kwargs['edit_key'] = key


        else:
            logging.info("(ProviderEducationHandler.get) No section object found for key %s" % key)
                
        
        self.render_cv(provider, **kwargs)
    
    @provider_required
    def post(self, vanity_url=None, section=None, operation=None, key=None):

        # instantiate and fill the section form
        section_form = self.forms[section]().get_form(self.request.POST)

        provider = db.get_provider_from_vanity_url(vanity_url)

        if section_form.validate():
            # Store section
            
            if operation == 'add':
                section_object = self.objs[section]()
                    
                section_form.populate_obj(section_object)

                section_object.provider = provider.key
                section_object.put()
                
                # stored eduction
                logging.debug("(ProviderEducationHandler.post) Stored section %s key=%s" % (section, section_object.key))

            if operation == 'edit':
                section_key = ndb.Key(urlsafe=key)
        
                if section_key:
                    section_object = section_key.get()
                    section_form.populate_obj(section_object)
                    section_object.provider = provider.key
                    section_object.put()
                    
                    # stored eduction
                    logging.info("(ProviderEducationHandler.post) Stored section %s key=%s" % (section, section_object.key))
                else:
                    logging.info("(ProviderEducationHandler.post) No section object found for key %s" % key)

            # success, empty forms so you can add another one            
            kwargs = self.generate_blank_forms()

            self.render_cv(provider, success_message=saved_message, **kwargs)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit CV: %s %s success" % (operation, section))

        else:            
            kwargs = {}
            for key in self.forms:
                if key == section:
                    # this one has errors
                    kwargs[key + "_form"] = section_form
                else:
                    # blank form
                    kwargs[key + '_form'] = self.forms[key]().get_form()
            
            if operation == 'edit':
                kwargs['edit'] = section
            
            self.render_cv(provider, **kwargs)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit CV: %s %s validation error" % (operation, section))


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
            
            
# BOOKING AND SCHEDULE STUFF
# *************************************

class ProviderBookingsHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        if provider:
            self.render_bookings(self, provider)





class ProviderScheduleHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        availableIds = provider.getAvailableScheduleIds()
        logging.info('available ids' + str(availableIds))
        self.render_schedule(provider, availableIds)
           
    @provider_required
    def post(self, vanity_url=None):
        logging.debug('ProviderScheduleHandler POST')
        day_time = self.request.get('day_time')
        day, startTime, endTime = day_time.split('-')
        operation = self.request.get('operation')
        logging.info("SAVE SCHEDULE: " + vanity_url + " " + day + "-" + startTime + "-" + endTime + " " + operation)
        
        provider = db.get_provider_from_vanity_url(vanity_url)
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



