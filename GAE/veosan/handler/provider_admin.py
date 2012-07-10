# -*- coding: utf-8 -*-
import logging
# GAE
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
# veo
from base import BaseHandler
import data.db as db
from data.model import Note
from forms.provider import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm, ProviderNoteForm
from handler.auth import admin_required
from util import saved_message

class ProviderAdminBaseHandler(BaseHandler):

    def render_profile(self, provider, profile_form, **kw):
        self.render_template('provider/profile.html', provider=provider, form=profile_form, **kw)
    
    def render_address(self, provider, address_form, **kw):
        upload_url = blobstore.create_upload_url('/admin/provider/address/upload')
        uploadForm = ProviderPhotoForm(self.request.GET)
        self.render_template('provider/address.html', provider=provider, form=address_form, uploadForm=uploadForm, upload_url=upload_url, **kw)
       
    def render_administration(self, provider, **kw):
        self.render_template('provider/administration.html', provider=provider, **kw)
    
    def render_notes(self, provider, **kw):
        notes = provider.get_notes()
        logging.info('Notes count %s' % notes.count())
        new_note_form = ProviderNoteForm()
        self.render_template('provider/notes.html', provider=provider, notes=notes, form=new_note_form, **kw)       
        

class ProviderEditProfileHandler(ProviderAdminBaseHandler):
    
    @admin_required
    def get(self, vanity_url = None):
        provider = None
        
        if vanity_url:
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            logging.info("(ProviderEditProfileHandler.get) Edit profile for provider %s" % provider.email)
            
            form = ProviderProfileForm(obj=provider)
            self.render_profile(provider, profile_form=form)
    
    # admin_required
    def post(self, vanity_url = None):
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
    def get(self, vanity_url = None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        logging.info("provider dump before edit:" + str(vars(provider)))
        form = ProviderAddressForm(obj=provider)
        self.render_address(provider, address_form=form)

    # admin_required
    def post(self, vanity_url = None):
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
    def get(self, vanity_url = None):
        provider = db.get_provider_from_vanity_url(vanity_url)
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


class ProviderAccountFeaturesHandler(ProviderAdminBaseHandler):
    def post(self, feature_switch=None):
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        
        # validate features that can be switched
        if feature_switch in ['booking_enabled', 'address_enabled']:
            
            # toggle state
            current_state = getattr(provider, feature_switch)
            
            if current_state:           
                setattr(provider, feature_switch, False)
                success_message = 'feature %s is now set to %s' % (feature_switch, False)
                provider.add_note('%s = False' % feature_switch)
                    
            else:
                setattr(provider, feature_switch, True)
                success_message = 'feature %s is now set to %s' % (feature_switch, True)
                provider.add_note('%s = True' % feature_switch)

            provider.put()
            
            self.render_administration(provider, success_message=success_message)

        else:
            logging.error('Received unknown feature switch : %s' % feature_switch)


class ProviderNotesHandler(ProviderAdminBaseHandler):
    
    @admin_required
    def get(self):
        provider = db.get_from_urlsafe_key(self.request.get('key')) 
        if users.is_current_user_admin():
            self.render_notes(provider)
        else:
            logging.info("Not Admin: Can't see provider notes page")
            
    def post(self):
        if users.is_current_user_admin():
            urlsafe_key = self.request.get('provider_key')
            provider = db.get_from_urlsafe_key(urlsafe_key)
            logging.info('type %s' % self.request.get('note_type'))
            provider.add_note(self.request.get('body'), note_type=self.request.get('note_type'))
            self.render_notes(provider)
        else:
            logging.info("Not Admin: Can't see provider notes page")
            