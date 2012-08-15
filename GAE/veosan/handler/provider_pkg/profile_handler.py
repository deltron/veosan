from handler.auth import provider_required
from forms.provider import ProviderProfileForm, ProviderPhotoForm
import logging
from data import db, search_index
from handler.provider import ProviderBaseHandler
from util import saved_message
from google.appengine.ext.webapp import blobstore_handlers


class ProviderEditProfileHandler(ProviderBaseHandler):

    @provider_required    
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        profile_form = ProviderProfileForm().get_form(obj=provider)
        
        logging.debug("(ProviderEditProfileHandler.get) Edit profile for provider %s" % provider.email)

        self.render_profile(provider, profile_form=profile_form)
    
    @provider_required    
    def post(self, vanity_url=None):
        form = ProviderProfileForm().get_form(self.request.POST)
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            provider_key = db.storeProvider(provider, self.request.POST, form=form)
            provider = provider_key.get()
            
            self.render_profile(provider, profile_form=form, success_message=saved_message)

            # log the event
            self.log_event(user=provider.user, msg="Edit Profile: Success")
            
            # update the index
            search_index.IndexProvider(provider)

        else:
            # show error
            provider = db.get_provider_from_vanity_url(vanity_url)
            self.render_profile(provider, profile_form=form)
            
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

