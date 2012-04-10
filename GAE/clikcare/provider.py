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
        
    def render_schedule(self, provider, **extra):
        hours = util.getTimesList()
        days = util.getWeekdays()
        self.render_template('provider/schedule.html', p=provider, hours=hours, days=days, **extra)
        
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
            # show errors
            self.render_address(provider, address_form=form)


class ProviderAddressUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        uploadForm = ProviderPhotoForm(self.request.POST)
        upload_files = self.get_uploads(uploadForm.profilePhoto.name)[0]
        
        logging.info("Uploaded blob key: %s" % upload_files.key())
        
        # Pseudocode to implement when ready :
        
        # 1. get Provider ID from the session
        # 2. store upload_files.key() in the Provider's record, update database        
        # 3. render the address form again with the updated photo
        
        # provider.profilePhotoBlobKey = upload_files.key()
        # data.storeProvider(provider)
        # self.render_template('patient/address.html', form=form)
        
        self.redirect('/serve/%s' % upload_files.key()) 
    #    self.render_template('patient/address.html', form=form) 

# temporary - to test image upload
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


# handle schedule changes like this http://tutorialzine.com/2011/04/app-engine-series-4-controllers/
class ProviderScheduleHandler(ProviderBaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            # edit provider
            provider = Provider.get(key)
            self.render_schedule(provider)
        else:
            logging.info("Missing key")
            
    def post(self):
        key = self.request.get('provider_key')
        day_time = self.request.get('day_time')
        day = day_time[0]
        time = day_time[2:]
        operation = self.request.get('operation')
        logging.info("SAVE SCHEDULE: " + key + " " + day + "-" + time + " " + operation)
        
        provider = Provider.get(key)
        if (operation == 'add'):
            s = Schedule()
            s.provider = provider
            s.day = int(day)
            s.time = int(time)
            s.put()
        elif (operation == 'remove'):
            provider.schedule.filter('day = ', day).filter('time = ', time).get().delete()
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
        
        
        
        
        
        
