# -*- coding: utf-8 -*-
import logging
# GAE
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
#clik
from base import BaseHandler
import data.db as db
from forms.provider import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm
from data.model import Provider
import util
from handler.auth import admin_required

class ProviderAdminBaseHandler(BaseHandler):
    def render_profile(self, provider, profile_form, **extra):
        self.render_template('provider/profile.html', p=provider, form=profile_form, **extra)
    
    def render_address(self, provider, address_form, **extra):
        upload_url = blobstore.create_upload_url('/provider/address/upload')
        uploadForm = ProviderPhotoForm(self.request.GET)
        self.render_template('provider/address.html', p=provider, form=address_form, uploadForm=uploadForm, upload_url=upload_url, **extra)
       
    def render_administration(self, provider, **extra):
        self.render_template('provider/administration.html', p=provider, **extra)
           

class ProviderEditProfileHandler(ProviderAdminBaseHandler):
    
    @admin_required
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
          

class ProviderEditAddressHandler(ProviderAdminBaseHandler):
    
    @admin_required
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
        provider.profile_photo_blob_key = upload_files.key()
        Provider.put(provider)
        # redirect to address edit page        
        self.redirect(provider.get_edit_link('address')) 

class ProviderAdministrationHandler(ProviderAdminBaseHandler):
    
    @admin_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))   
        if users.is_current_user_admin():
            self.render_administration(provider)
        else:
            logging.info("Not Admin: Can't see provider administration page")
        
            
