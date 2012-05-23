# -*- coding: utf-8 -*-
import logging
from base import BaseHandler
import data.db as db
import urllib
from forms import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm, ProviderTermsForm, ProviderLoginForm
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from data.model import Provider, Schedule
import util

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
    
    def render_bookings(self, provider, bookings, **extra):
        self.render_template('provider/bookings.html', p=provider, bookings=bookings, **extra)
            
    def render_terms(self, provider, terms_form, **extra):
        self.render_template('provider/provider_terms.html', p=provider, form=terms_form, **extra)

    def render_administration(self, provider, **extra):
        self.render_template('provider/administration.html', p=provider, **extra)
           

class ProviderEditProfileHandler(ProviderBaseHandler):
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        logging.info("provider dump before edit:" + str(vars(provider)))
        form = ProviderProfileForm(obj=provider)
        self.render_profile(provider, profile_form=form)
    
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
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        logging.info("provider dump before edit:" + str(vars(provider)))
        form = ProviderAddressForm(obj=provider)
        self.render_address(provider, address_form=form)

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
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        availableIds = provider.getAvailableScheduleIds()
        logging.info('available ids' + str(availableIds))
        self.render_schedule(provider, availableIds)
            
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
            s.provider = provider
            s.day = int(day)
            s.startTime = int(startTime)
            s.endTime = int(endTime)
            s.put()
        elif (operation == 'remove'):
            s_to_delete = provider.schedule.filter('day = ', int(day)).filter('startTime = ', int(startTime)).get()
            logging.info('deleting schedule' + str(s_to_delete))
            if (s_to_delete):
                s_to_delete.delete()
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
            provider.terms_agreement = self.request.get('terms_agreement')
            provider.put()
            # TODO Add Welcome Message and invitation to review profile and set schedule
            redirect_url = provider.get_edit_link(section='profile')
            logging.info(redirect_url)
            self.redirect(redirect_url)
        else:
            self.render_terms(provider, terms_form=terms_form)


class ProviderBookingsHandler(ProviderBaseHandler):
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        bookings = db.fetch_future_bookings(provider)   
        logging.info('Bookings:' + str(bookings))
        self.render_bookings(provider, bookings)


class ProviderAdministrationHandler(ProviderBaseHandler):
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))   
        if users.is_current_user_admin():
            self.render_administration(provider)
        else:
            logging.info("Not Admin: Can't see provider administration page")


class ProviderLoginHandler(ProviderBaseHandler):
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        login_form = ProviderLoginForm(obj=provider)
        self.render_login(provider, login_form=login_form) 
    
    def post(self):
        form = ProviderLoginForm(self.request.POST)
        if form.validate():
            # Retrieve Provider from email address
            email = form.email.data
            provider = db.getProviderFromEmail(email)
            logging.info("provider dump before edit:" + str(vars(provider)))
            self.render_schedule(provider)
        else:
            # TODO redisplay Login page on failed validation
            logging.info('ProviderLoginForm validation failed')
            pass
        
        
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
        
        
        
        
