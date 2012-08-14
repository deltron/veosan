import logging
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from webapp2_extras.i18n import lazy_gettext as _

# veo
import data.db as db
from data.model import Schedule, Education, Experience, ContinuingEducation, \
    ProfessionalOrganization, ProfessionalCertification, Invite
from forms.provider import ProviderAddressForm, ProviderEducationForm, ProviderContinuingEducationForm, ProviderExperienceForm, ProviderProfileForm, ProviderPhotoForm, \
    ProviderCertificationForm, ProviderOrganizationForm, ProviderScheduleForm, \
    ProviderVanityURLForm, ProviderInviteForm
from base import BaseHandler
from handler.auth import provider_required
import util
from util import saved_message
from utilities import time
from forms.booking import EmailOnlyBookingForm
from data import search_index
from google.appengine.api import search
import urlparse
import mail
from handler import auth

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
        address_form = ProviderAddressForm().get_form(obj=provider)
        vanity_url_form = ProviderVanityURLForm().get_form(obj=provider)

        self.render_address(provider, address_form=address_form, vanity_url_form=vanity_url_form)

    @provider_required
    def post(self, vanity_url=None):
        form = ProviderAddressForm().get_form(self.request.POST)
        
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            form.populate_obj(provider)
            provider.put()

            vanity_url_form = ProviderVanityURLForm().get_form(obj=provider)

            self.render_address(provider, address_form=form, vanity_url_form=vanity_url_form, success_message=saved_message)

            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Success")

            # update the index
            search_index.IndexProvider(provider)

        else:
            # show validation error
            provider = db.get_provider_from_vanity_url(vanity_url)
            vanity_url_form = ProviderVanityURLForm().get_form(obj=provider)

            self.render_address(provider, address_form=form, vanity_url_form=vanity_url_form)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Validation Error")



        


class ProviderChangeURLHandler(ProviderBaseHandler):
    @provider_required
    def post(self, vanity_url=None):
        form = ProviderVanityURLForm().get_form(self.request.POST)
        
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            form.populate_obj(provider)
            
            provider.put()

            self.redirect('/provider/address/' + provider.vanity_url)

            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Success")

        else:
            # show validation error
            provider = db.get_provider_from_vanity_url(vanity_url)
            address_form = ProviderAddressForm().get_form(obj=provider)

            self.render_address(provider, address_form=address_form, vanity_url_form=form)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Validation Error")




class ProviderEditProfileHandler(ProviderBaseHandler):

    @provider_required    
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        profile_form = ProviderProfileForm().get_form(obj=provider)
        
        logging.debug("(ProviderEditProfileHandler.get) Edit profile for provider %s" % provider.email)

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
            
            # update the index
            search_index.IndexProvider(provider)

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

#### CV Stuff

class ProviderCVHandler(ProviderBaseHandler):
    forms = { 'education' : ProviderEducationForm,
              'experience' : ProviderExperienceForm,
              'continuing_education' : ProviderContinuingEducationForm,
              'organization' : ProviderOrganizationForm,
              'certification' : ProviderCertificationForm,
            }

    objs = { 'education' : Education,
             'experience' : Experience,
             'continuing_education' : ContinuingEducation,
             'organization' : ProfessionalOrganization,
             'certification' : ProfessionalCertification,
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
        section_object_key = None

        if key:
            section_object_key = ndb.Key(urlsafe=key)
        
        if section_object_key:
            if operation == 'delete':
                logging.info("(ProviderEducationHandler.get) Delete section %s key=%s" % (section, key))
                            
                section_object_key.delete()
                
                # success, empty forms so you can play again            
                kwargs = self.generate_blank_forms()
            
                # log the event
                self.log_event(user=provider.user, msg="Edit CV: %s %s success" % (operation, section))

            if operation == 'edit':
                logging.info("(ProviderEducationHandler.get) Edit section %s key=%s" % (section, key))
                
                # get the object
                obj = section_object_key.get()
                
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
                new_section_object = self.objs[section]()
                    
                section_form.populate_obj(new_section_object)

                new_section_object.provider = provider.key
                new_section_object.put()
                
                # stored eduction
                logging.debug("(ProviderEducationHandler.post) Stored section %s key=%s" % (section, new_section_object.key))

            if operation == 'edit':
                section_object_key = ndb.Key(urlsafe=key)
        
                if section_object_key:
                    section_object = section_object_key.get()
                    section_form.populate_obj(section_object)
                    section_object.put()
                    
                    # stored
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
            for k in self.forms:
                if k == section:
                    # this one has errors
                    kwargs[k + '_form'] = section_form
                else:
                    # blank form
                    kwargs[k + '_form'] = self.forms[k]().get_form()
            
            if operation == 'edit':
                kwargs['edit'] = section
                kwargs['edit_key'] = key
            
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
            


class WelcomeHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None, disable=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        if disable == 'disable':
            provider.display_welcome_page = False
            provider.put()
            self.redirect('/provider/profile/' + provider.vanity_url)
            return # don't render template after redirect

        self.render_template("provider/welcome.html", provider=provider)

class SocialHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        provider_invite_form = ProviderInviteForm().get_form()

        self.render_template("provider/network.html", provider=provider, provider_invite_form=provider_invite_form)

    @provider_required
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        form = ProviderInviteForm().get_form(self.request.POST)
        if form.validate():
            invite = Invite()
            form.populate_obj(invite)
            
            # associate provider to invite
            invite.provider = provider.key
            
            # create a token for this invite that will be used to pre-populate the signup form
            invite.token = self.create_token(invite.email)
            
            # save
            invite.put()
            
            # create an invite url
            url_obj = urlparse.urlparse(self.request.url)
            invite_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/invite/' + invite.token, '', '', ''))
            logging.info('(SocialHandler.post) unique invite URL:' + invite_url)

            # send the actual email...
            mail.email_invite(self.jinja2, invite, invite_url)
            
            # all good
            message = "Invitation sent to %s %s (%s)" % (invite.first_name, invite.last_name, invite.email)
            
            # new form for next invite
            provider_invite_form = ProviderInviteForm().get_form()
            self.render_template("provider/network.html", success_message=message, provider=provider, provider_invite_form=provider_invite_form)
        else:
            self.render_template("provider/network.html", provider=provider, provider_invite_form=form)

class ProviderPublicProfileConnectHandler(ProviderBaseHandler):
    def get(self, vanity_url=None):
        provider_target = db.get_provider_from_vanity_url(vanity_url)
        
        user_source = self.get_current_user()
        if user_source and auth.PROVIDER_ROLE in user_source.roles:
            provider_source = db.get_provider_from_user(user_source)
        
            provider_source.provider_network.append(provider_target.key)
            provider_source.put()
            
            message = "You are now connected!"
            self.render_public_profile(provider=provider_target, success_message=message)
        else:
            # redirect to login page if not logged in
            # TODO: should know to continue to connect after login and go back to profile page
            self.redirect("/login")
        
        
    

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

        
        
        

