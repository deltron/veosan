# -*- coding: utf-8 -*-
import logging
from base import BaseHandler
import db
from forms import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm
import urllib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from data import Provider
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
        
    def render_terms(self, provider, **extra):
        self.render_template('provider/terms.html', p=provider, **extra)
        

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
        # Store Provider
        key = db.storeProvider(self.request)
        provider = Provider.get(key)
        self.render_schedule(provider)


class ProviderTermsHandler(ProviderBaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            # edit provider
            provider = Provider.get(key)
            self.render_terms(provider)
        else:
            logging.info("Missing key")
            
        
        
        
        
