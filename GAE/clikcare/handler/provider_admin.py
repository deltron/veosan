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
from handler.auth import admin_required
from util import saved_message

class ProviderAdminBaseHandler(BaseHandler):

    def render_profile(self, provider, profile_form, **extra):
        self.render_template('provider/profile.html', provider=provider, form=profile_form, **extra)
    
    def render_address(self, provider, address_form, **extra):
        upload_url = blobstore.create_upload_url('/admin/provider/address/upload')
        uploadForm = ProviderPhotoForm(self.request.GET)
        self.render_template('provider/address.html', provider=provider, form=address_form, uploadForm=uploadForm, upload_url=upload_url, **extra)
       
    def render_administration(self, provider, **extra):
        self.render_template('provider/administration.html', provider=provider, **extra)
           

class ProviderEditProfileHandler(ProviderAdminBaseHandler):
    
    @admin_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        logging.info("provider dump before edit:" + str(vars(provider)))
        form = ProviderProfileForm(obj=provider)
        self.render_profile(provider, profile_form=form)
    
    # admin_required
    def post(self):
        form = ProviderProfileForm(self.request.POST)
        if form.validate():
            # Store Provider
            key = db.storeProvider(self.request.POST)
            provider = key.get()
            self.render_profile(provider, profile_form=form, success_message=saved_message)
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

    # admin_required
    def post(self):
        form = ProviderAddressForm(self.request.POST)
        if form.validate():
            # Store Provider
            provider_key = db.storeProvider(self.request.POST)
            provider = provider_key.get()
            self.render_address(provider, address_form=form, success_message=saved_message)
        else:
            # show validation error
            provider = db.getProvider(self.request)
            self.render_address(provider, address_form=form)


class ProviderAddressUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    
    def post(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))
        logging.info("(ProviderAddressUploadHandler.post) Found provider: %s %s" % (provider.first_name, provider.last_name))
        uploadForm = ProviderPhotoForm(self.request.POST)
        upload_files = self.get_uploads(uploadForm.profilePhoto.name)[0]
        logging.info("(ProviderAddressUploadHandler.post) Uploaded blob key: %s " % upload_files.key())
        provider.profile_photo_blob_key = upload_files.key()
        provider.put()
        
        # redirect to address edit page        
        self.redirect(provider.get_edit_link(str('/admin/provider/address'))) 

class ProviderAdministrationHandler(ProviderAdminBaseHandler):
    
    @admin_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key'))   
        if users.is_current_user_admin():
            self.render_administration(provider)
        else:
            logging.info("Not Admin: Can't see provider administration page")
        

  
class ProviderEnableHandler(ProviderAdminBaseHandler):
    def post(self):
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        
        success_message = ''
        
        # toggle provider state
        if provider.enable:
            provider.enable = False
            success_message = 'Provider is now disabled'            
        else:
            provider.enable = True        
            success_message = 'Provider is now enabled'            

        provider.put()

        self.render_administration(provider, success_message=success_message)

