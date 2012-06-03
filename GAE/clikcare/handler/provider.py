# -*- coding: utf-8 -*-
import logging
import urllib
from datetime import date
# GAE
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
#clik
from base import BaseHandler
import data.db as db
from forms.provider import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm, ProviderTermsForm, ProviderPasswordForm
from data.model import Provider, Schedule
import util, mail
from handler.auth import provider_required, admin_required

def parseRefererSection(request):
    referer = request.environ['HTTP_REFERER']
    logging.info("referer:" + referer)
    section = referer.split('/')[-1]
    return section

class ProviderBaseHandler(BaseHandler):
    def render_profile(self, provider, profile_form, **extra):
        self.render_template('provider/profile.html', p=provider, form=profile_form, **extra)
    
    def render_address(self, provider, address_form, **extra):
        upload_url = blobstore.create_upload_url('/provider/address/upload')
        uploadForm = ProviderPhotoForm(self.request.GET)
        self.render_template('provider/address.html', p=provider, form=address_form, uploadForm=uploadForm, upload_url=upload_url, **extra)
        
    def render_schedule(self, provider, availableIds, **extra):
        timeslots = util.getScheduleTimeslots()
        days = util.getWeekdays()
        self.render_template('provider/schedule.html', p=provider, availableIds=availableIds, timeslots=timeslots, days=days, **extra)
    
    def render_bookings(self, provider, **extra):
        bookings = db.fetch_future_bookings(provider)   
        logging.info('Bookings:' + str(bookings))
        self.render_template('provider/bookings.html', p=provider, bookings=bookings, **extra)
            
    def render_terms(self, provider, terms_form, **extra):
        self.render_template('provider/provider_terms.html', p=provider, form=terms_form, **extra)

    def render_password(self, provider, password_form=None, **extra):
        if not password_form:
            password_form = ProviderPasswordForm()
        self.render_template('provider/password.html', p=provider, form=password_form, **extra)
        
    def render_administration(self, provider, **extra):
        self.render_template('provider/administration.html', p=provider, **extra)
           

class ProviderEditProfileHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        logging.info("provider dump before edit:" + str(vars(provider)))
        form = ProviderProfileForm(obj=provider)
        self.render_profile(provider, profile_form=form)
    
    @provider_required
    def post(self):
        form = ProviderProfileForm(self.request.POST)
        if form.validate():
            # Store Provider
            key = db.storeProvider(self.request.POST)
            provider = key.get()
            self.render_profile(provider, profile_form=form, success_message=util.saved_message)
        else:
            # show error
            provider = db.getProvider(self.request)
            self.render_profile(provider, profile_form=form)
          

class ProviderEditAddressHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        logging.info("provider dump before edit:" + str(vars(provider)))
        form = ProviderAddressForm(obj=provider)
        self.render_address(provider, address_form=form)

    @provider_required
    def post(self):
        form = ProviderAddressForm(self.request.POST)
        if form.validate():
            # Store Provider
            key = db.storeProvider(self.request.POST)
            provider = key.get()
            self.render_address(provider, address_form=form, success_message=util.saved_message)
        else:
            # show validation error
            provider = db.getProvider(self.request)
            self.render_address(provider, address_form=form)


class ProviderAddressUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    
    @provider_required
    def post(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        logging.info("Found provider: %s %s" % (provider.first_name, provider.last_name))
        uploadForm = ProviderPhotoForm(self.request.POST)
        upload_files = self.get_uploads(uploadForm.profilePhoto.name)[0]
        logging.info("Uploaded blob key: %s " % upload_files.key())
        provider.profile_photo_blob = upload_files.key()
        Provider.put(provider)
        # redirect to address edit page        
        self.redirect(provider.get_edit_link('address')) 

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    ''' Serve a blob with key. call URL as
            /serve/xxx   where xxx = blob store key
    '''
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo(resource)
        self.send_blob(blob_info)


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
        urlsafe_key = self.request.get('provider_key')
        day_time = self.request.get('day_time')
        day, startTime, endTime = day_time.split('-')
        operation = self.request.get('operation')
        logging.info("SAVE SCHEDULE: " + urlsafe_key + " " + day + "-" + startTime + "-" + endTime + " " + operation)
        
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
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

class ProviderTermsHandler(ProviderBaseHandler):
    
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        terms_form = ProviderTermsForm(obj=provider)
        self.render_terms(provider, terms_form=terms_form)
    
    def post(self):
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        terms_form = ProviderTermsForm(self.request.POST)
        if terms_form.validate():
            # Save signature and terms agreement
            provider.terms_agreement = self.request.get('terms_agreement') == u'True'
            provider.terms_date = date.today()
            provider.put()
            # Go to the password selection page
            self.render_password(provider)
        else:
            self.render_terms(provider, terms_form=terms_form)


class ProviderPasswordHandler(ProviderBaseHandler):
    def get(self):
        '''
            TODO: Display page in the context of the Provider profile (with tabs at the top)
        '''
        logging.info('GET not implemented on /provider/password')
        pass
            
    def post(self):
        '''
            Create user and link it to the Provider
        '''
        logging.info('POST provider password')
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        password_form = ProviderPasswordForm(self.request.POST)
        if password_form.validate():
            # Create User in Auth system
            # we are not reading email from form
            email = provider.email
            password = self.request.get('password')
            user = self.create_user(email, password)
            if user:
                # Link user to provider
                provider.user = user.key
                provider.put()
                mail.emailProviderWelcomeMessage(self.jinja2, provider)
                # Provider is Activated
                # login automatically
                self.login_user(email, password)
                # TODO Add Welcome Message and invitation to review profile and set schedule
                #redirect_url = provider.get_edit_link(section='profile')
                #self.redirect(redirect_url)
                welcome_message = _("Welcome to Clikcare! Please review your profile and open your schedule.")
                self.render_bookings(provider, success_message=welcome_message)
            else:
                logging.error('User not created. Probably because email already in Unique table.')
                # TODO add custom validation to tell user that email is already in use.
                error_message = 'User email is already taken. If you are already using this email for your patient profile, please inform us or use another email.'
                self.render_password(provider, password_form=password_form, error_message=error_message)
        else:
            self.render_password(provider, password_form=password_form)


class ProviderBookingsHandler(ProviderBaseHandler):
    
    @provider_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        
        self.render_bookings(provider)


class ProviderAdministrationHandler(ProviderBaseHandler):
    
    @admin_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))   
        if users.is_current_user_admin():
            self.render_administration(provider)
        else:
            logging.info("Not Admin: Can't see provider administration page")
        
        
class ProviderActivationHandler(ProviderBaseHandler):
    def get(self, activation_key=None):
        #parse URL to get activation key
        if (activation_key):
            provider = db.get_provider_from_activation_key(activation_key)
            # show terms page
            terms_form = ProviderTermsForm(obj=provider)
            self.render_terms(provider, terms_form=terms_form)
        else:
            logging.info('No activation key')
        
        
        
        
