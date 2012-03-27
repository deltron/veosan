# -*- coding: utf-8 -*-
import logging
from base import BaseHandler
import db
from forms import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm
import urllib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from data import Provider


class ProviderProfileHandler(BaseHandler):
    def get(self):
        form = ProviderProfileForm(self.request.POST)
        self.render_template('provider/profile.html', form=form)
    
    def post(self):
        form = ProviderProfileForm(self.request.POST)
        if form.validate():
            self.render_template('patient/profile.html', form=form) 
        else:
            self.render_template('patient/profile.html', form=form)


class ProviderAddressHandler(BaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            # edit provider
            logging.info("Edit provider. key:" + key)
            provider = Provider.get(key)
            # TODO make this work
            form = ProviderAddressForm(provider)
        else:
            # new provider
            logging.info("Blank form for new provider")
            form = ProviderAddressForm(self.request.GET)
            upload_url = blobstore.create_upload_url('/provider/address/upload')
            uploadForm = ProviderPhotoForm(self.request.GET)
        self.render_template('provider/address.html', form=form, uploadForm=uploadForm, upload_url=upload_url)
        
    def post(self):
        form = ProviderAddressForm(self.request.POST)
        upload_url = blobstore.create_upload_url('/provider/address/upload')
        uploadForm = ProviderPhotoForm(self.request.POST)
        if form.validate():
            # Store Provider Address
            db.storeProvider(self.request)
            self.render_template('provider/address.html', form=form, uploadForm=uploadForm, upload_url=upload_url) 
        else:
            # show errors
            self.render_template('provider/address.html', form=form, uploadForm=uploadForm, upload_url=upload_url)


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

class ProviderScheduleHandler(BaseHandler):
    def get(self):
        self.render_template('provider/schedule.html', name=self.request.get('name'))

class ProviderTermsHandler(BaseHandler):
    def get(self):
        self.render_template('provider/terms.html', name=self.request.get('name'))
