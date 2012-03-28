# -*- coding: utf-8 -*-
import logging
from base import BaseHandler
import db
from forms import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm
import urllib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from data import Provider

def parseRefererSection(request):
    referer = request.environ['HTTP_REFERER']
    logging.info("referer:" + referer)
    section = referer.split('/')[-1]
    return section

class BaseProviderHandler(BaseHandler):
    def render_profile(self, profile_form, **extra):
        self.render_template('provider/profile.html', form=profile_form, **extra)
    
    def render_address(self, address_form, **extra):
        upload_url = blobstore.create_upload_url('/provider/address/upload')
        uploadForm = ProviderPhotoForm(self.request.GET)
        self.render_template('provider/address.html', form=address_form, uploadForm=uploadForm, upload_url=upload_url, **extra)
        

class ProviderNewHandler(BaseProviderHandler):
    def get(self):
        # todo: save referer url and redicrect there when new flow is finished
        
        #if (parseSection(self.request.) != 'profile'):
        #    self.redirect('/provider/new/profile')
        logging.info("Blank profile form for new provider")
        profile_form = ProviderProfileForm(self.request.POST)
        self.render_profile(profile_form, flow='new')
        
    def post(self):
        section = parseRefererSection(self.request)
        logging.info('Coming from section' + section)
        if (section == 'profile'):
            # step 1
            profile_form = ProviderProfileForm(self.request.POST)
            if profile_form.validate():
                logging.info('profile form validated. going to step 2, address form')
                # create provider and go to next page: address
                provider_key = db.storeProvider(self.request)
                address_form = ProviderAddressForm(self.request.POST)
                self.render_address(address_form, provider_key=provider_key, flow='new')
            else:
                # validation failed. redraw profile form
                self.render_profile(profile_form)
        elif (section == 'address'):
            # step 2
            logging.info("Post of Address");
            address_form = ProviderAddressForm(self.request.POST)
            if address_form.validate():
                # Store Provider Address
                db.storeProvider(self.request)
                # redirect to original referer
                self.redirect('/admin')
            else:
                self.render_address(address_form, provider_key=provider_key, flow='new')
            


class ProviderEditProfileHandler(BaseHandler):
    def get(self):
        form = ProviderProfileForm(self.request.POST)
        self.render_template('provider/profile.html', form=form)
    
    def post(self):
        form = ProviderProfileForm(self.request.POST)
        if form.validate():
            self.render_template('patient/profile.html', form=form) 
        else:
            self.render_template('patient/profile.html', form=form)
          

class ProviderEditAddressHandler(BaseHandler):
    def get(self):
        key = self.request.get('key')
        if (key):
            # edit provider
            logging.info("Edit provider. key:" + str(key))
            provider = Provider.get(key)
            logging.info("pprint:" + str(vars(provider)))
            logging.info('Editing provider: ' + str(provider))
            form = ProviderAddressForm(obj=provider)
            upload_url = blobstore.create_upload_url('/provider/address/upload')
            uploadForm = ProviderPhotoForm(self.request.GET)
            self.render_template('provider/address.html', form=form, uploadForm=uploadForm, upload_url=upload_url)
        else:
            logging.info("Edit Address. Missing key")
            # missing key. Route to new ?

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
        
        
        
