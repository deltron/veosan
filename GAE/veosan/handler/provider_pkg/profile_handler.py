from handler.auth import provider_required
from forms.provider import ProviderProfileForm, ProviderPhotoForm, ProviderServiceForm
import logging
from data import db
from handler.provider import ProviderBaseHandler
from util import saved_message
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from data.model_pkg.booking_schedule_model import ProviderService


class ProviderEditProfileHandler(ProviderBaseHandler):

    @provider_required    
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        profile_form = ProviderProfileForm().get_form(obj=provider)
        service_form = ProviderServiceForm().get_form()
        
        logging.debug("(ProviderEditProfileHandler.get) Edit profile for provider %s" % provider.email)

        self.render_profile(provider, profile_form=profile_form, service_form=service_form)
    
    @provider_required    
    def post(self, vanity_url=None):
        form = ProviderProfileForm().get_form(self.request.POST)
        service_form = ProviderServiceForm().get_form()

        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            form.populate_obj(provider)
            provider.put()
            
            provider_user = provider.user.get()
            if provider_user.language != provider.profile_language:
                provider_user.language = provider.profile_language
                provider_user.put()
                self.set_language(provider.profile_language)
            
            self.render_profile(provider, profile_form=form, service_form=service_form, success_message=saved_message)

            # log the event
            self.log_event(user=provider.user, msg="Edit Profile: Success")

        else:
            # show error
            provider = db.get_provider_from_vanity_url(vanity_url)
            self.render_profile(provider, profile_form=form, service_form=service_form)
            
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


class ProviderServiceHandler(ProviderBaseHandler):

    @provider_required
    def get(self, vanity_url=None, operation=None, key=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        service_object_key = None

        if key:
            service_object_key = ndb.Key(urlsafe=key)
            
        if service_object_key:
            if operation == 'delete':
                            
                service_object_key.delete()
                
                self.redirect('/provider/profile/%s' % provider.vanity_url) 

            elif operation == 'edit':                
                # get the object
                obj = service_object_key.get()
                
                # populate the form
                service_form = ProviderServiceForm().get_form(obj=obj)
                profile_form = ProviderProfileForm().get_form(obj=provider)
                
                self.render_profile(provider, profile_form=profile_form, service_form=service_form, edit= 'service', edit_key = key)
                
                                
            else:
                self.redirect('/provider/profile/%s' % provider.vanity_url) 
            
        


    @provider_required
    def post(self, vanity_url=None, operation=None, key=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        service_form = ProviderServiceForm().get_form(self.request.POST)
        if service_form.validate():
            if operation == 'add':
                service_object = ProviderService()
                service_form.populate_obj(service_object)
                service_object.provider = provider.key
                service_object.put()

            if operation == 'edit':
                service_object_key = ndb.Key(urlsafe=key)
        
                if service_object_key:
                    service_object = service_object_key.get()
                    service_form.populate_obj(service_object)
                    service_object.put()
            
            self.redirect('/provider/profile/%s' % provider.vanity_url) 
        else:
            profile_form = ProviderProfileForm().get_form(obj=provider)

            self.render_profile(provider, profile_form=profile_form, service_form=service_form)
