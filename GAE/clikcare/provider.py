# -*- coding: utf-8 -*-
import logging
from base import BaseHandler
import db
from forms import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm, ProviderTermsForm, ProviderLoginForm
import urllib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from data import Provider, Schedule
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
        self.render_template('provider/terms.html', p=provider, form=terms_form, **extra)
   
    def render_login(self, provider, login_form, **extra):
        self.render_template('provider/login.html', p=provider, form=login_form, **extra)
        

class ProviderEditProfileHandler(ProviderBaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            # edit provider
            provider = Provider.get(key)
            logging.info("provider dump before edit:" + str(vars(provider)))
            form = ProviderProfileForm(obj=provider)
            self.render_profile(provider, profile_form=form)
        else:
            logging.info("Missing key")
            # Add error message on page
    
    def post(self):
        form = ProviderProfileForm(self.request.POST)
        if form.validate():
            # Store Provider
            key = db.storeProvider(self.request)
            provider = Provider.get(key)
            self.render_profile(provider, profile_form=form)
        else:
            # show error
            provider = db.getProvider(self.request)
            self.render_profile(provider, profile_form=form)
          

class ProviderEditAddressHandler(ProviderBaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            # edit provider
            provider = Provider.get(key)
            logging.info("provider dump before edit:" + str(vars(provider)))
            
            form = ProviderAddressForm(obj=provider)
            self.render_address(provider, address_form=form)
        else:
            logging.info("Missing key")
            # missing key. Route to new ?

    def post(self):
        form = ProviderAddressForm(self.request.POST)
        #provider = Provider.get(key)
        if form.validate():
            # Store Provider
            key = db.storeProvider(self.request)
            provider = Provider.get(key)
            self.render_address(provider, address_form=form)
        else:
            # show error
            provider = db.getProvider(self.request)
            self.render_address(provider, address_form=form)


class ProviderAddressUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        key = self.request.get('key')
        logging.info("Looking for provider key: %s " % key)
        provider = Provider.get(key)
        logging.info("Found provider: %s %s" % (provider.firstName, provider.lastName))

        uploadForm = ProviderPhotoForm(self.request.POST)
        upload_files = self.get_uploads(uploadForm.profilePhoto.name)[0]
        logging.info("Uploaded blob key: %s " % upload_files.key())
        
        provider.profilePhotoBlob = upload_files.key()

        Provider.put(provider)
        
        # redirect to address edit page        
        self.redirect('/provider/address?key=%s' % key) 

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    ''' Serve a blob with key. call URL as
            /serve/xxx   where xxx = blob store key
    '''
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class ProviderScheduleHandler(ProviderBaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            # edit provider
            provider = Provider.get(key)
            availableIds = provider.getAvailableScheduleIds()
            logging.info('available ids' + str(availableIds))
            self.render_schedule(provider, availableIds)
        else:
            logging.info("Missing key")
            
    def post(self):
        key = self.request.get('provider_key')
        day_time = self.request.get('day_time')
        day, startTime, endTime = day_time.split('-')
        operation = self.request.get('operation')
        logging.info("SAVE SCHEDULE: " + key + " " + day + "-" + startTime + "-" + endTime + " " + operation)
        
        provider = Provider.get(key)
        if (operation == 'add'):
            s = Schedule()
            s.provider = provider
            s.day = int(day)
            s.startTime = int(startTime)
            s.endTime = int(endTime)
            s.put()
        elif (operation == 'remove'):
            s_to_delete = provider.schedule.filter('day = ', int(day)).filter('time = ', int(time)).get()
            logging.info('deleting schedule' + str(s_to_delete))
            if (s_to_delete):
                s_to_delete.delete()
            else:
                logging.error("Can't find schedule to delete")  
        else:
            logging.info('Wrong operation save schedule:' + operation)

class ProviderTermsHandler(ProviderBaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            # edit provider
            provider = Provider.get(key)
            terms_form = ProviderTermsForm(obj=provider)
            self.render_terms(provider, terms_form=terms_form)
        else:
            logging.info("Missing key")
            
        
class ProviderBookingsHandler(ProviderBaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            provider = Provider.get(key)
            bookings = provider.booking_set
            logging.info('Bookings:' + str(bookings))
            self.render_bookings(provider, bookings)
        else:
            logging.info("Missing provider key")


class ProviderLoginHandler(ProviderBaseHandler):
    def get(self):
        key = self.request.get('key')
        
        provider = None;
        
        if (key):
            # show provider name (from cookie?)
            provider = Provider.get(key)
           
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
        
        
        
        
        
        
