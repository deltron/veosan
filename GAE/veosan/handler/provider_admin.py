# -*- coding: utf-8 -*-
import logging
# GAE
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
# veo
from base import BaseHandler
import data.db as db
import data.db_util as db_util
from data.model import Note, Education, Experience, ContinuingEducation
from forms.provider import ProviderProfileForm, ProviderAddressForm, ProviderPhotoForm, ProviderNoteForm, ProviderStatusForm, ProviderEducationForm, ProviderContinuingEducationForm, ProviderExperienceForm
from handler.auth import admin_required
from util import saved_message

class ProviderAdminBaseHandler(BaseHandler):
    
    def render_cv(self, provider, **kw):
        self.render_template('provider/cv.html', provider=provider, **kw)

    def render_profile(self, provider, **kw):
        self.render_template('provider/profile.html', provider=provider, **kw)
    
    def render_address(self, provider, address_form, **kw):
        upload_url = blobstore.create_upload_url('/admin/provider/address/upload/%s' % provider.vanity_url)
        uploadForm = ProviderPhotoForm(self.request.GET)
        self.render_template('provider/address.html', provider=provider, form=address_form, uploadForm=uploadForm, upload_url=upload_url, **kw)
    
    @staticmethod
    def render_administration(handler, provider, **kw):
        status_form = ProviderStatusForm(obj=provider)
        handler.render_template('provider/administration.html', provider=provider, form=status_form, **kw)
    
    def render_notes(self, provider, **kw):
        notes = provider.get_notes().fetch(10)
        logging.info('Notes count %s' % len(notes))
        new_note_form = ProviderNoteForm()
        # create a form for each note
        for n in notes:
            n.edit_form = ProviderNoteForm(obj=n)
        self.render_template('provider/notes.html', provider=provider, notes=notes, form=new_note_form, **kw)       
        

class ProviderEditProfileHandler(ProviderAdminBaseHandler):
    
    @admin_required
    def get(self, vanity_url=None):
        provider = None
        
        if vanity_url:
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            logging.info("(ProviderEditProfileHandler.get) Edit profile for provider %s" % provider.email)
            
            profile_form = ProviderProfileForm(obj=provider)
            education_form = ProviderEducationForm()
            experience_form = ProviderExperienceForm()
            
            self.render_profile(provider, profile_form=profile_form, education_form=education_form, experience_form=experience_form)
    
    # admin_required
    def post(self, vanity_url=None):
        form = ProviderProfileForm(self.request.POST)
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            provider_key = db.storeProvider(provider, self.request.POST)
            provider = provider_key.get()
            self.render_profile(provider, profile_form=form, success_message=saved_message)
        else:
            # show error
            provider = db.get_provider_from_vanity_url(vanity_url)
            self.render_profile(provider, profile_form=form)

class ProviderCVHandler(ProviderAdminBaseHandler):
    forms = { 'education' : ProviderEducationForm,
              'experience' : ProviderExperienceForm,
              'continuing_education' : ProviderContinuingEducationForm,
            }

    objs = { 'education' : Education,
             'experience' : Experience,
             'continuing_education' : ContinuingEducation
            }

    def generate_blank_forms(self):
        kwargs = {}
        
        # create blank forms
        for key in self.forms:
            kwargs[key + '_form'] = self.forms[key]()

        return kwargs

    @admin_required
    def get(self, vanity_url=None, section=None, operation=None, key=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        if operation == 'delete':
            logging.info("(ProviderEducationHandler.get) Delete section %s " % key)
            
            section_key = ndb.Key(urlsafe=key)
            
            if section_key:
                section_key.delete()
            else:
                logging.info("(ProviderEducationHandler.get) No section object found for key %s" % key)
            
        # success, empty forms so you can play again            
        kwargs = self.generate_blank_forms()
        
        self.render_cv(provider, **kwargs)
    
    # admin_required
    def post(self, vanity_url=None, section=None, operation=None, key=None):

        # instantiate and fill the section form
        section_form = self.forms[section](self.request.POST)

        provider = db.get_provider_from_vanity_url(vanity_url)

        if section_form.validate():
            # Store section
            
            if operation == 'add':
                section_object = self.objs[section]()
                    
                db_util.set_all_properties_on_entity_from_multidict(section_object, self.request.POST)
                section_object.provider = provider.key
                section_object.put()
                
                # stored eduction
                logging.info("(ProviderEducationHandler.post) Stored section %s key=%s" % (section, section_object.key))

            # success, empty forms so you can add another one            
            kwargs = self.generate_blank_forms()

            self.render_cv(provider, success_message=saved_message, **kwargs)
        else:            
            kwargs = {}
            for key in self.forms:
                if key == section:
                    # this one has errors
                    kwargs[key + "_form"] = section_form
                else:
                    # blank form
                    kwargs[key + '_form'] = self.forms[key]()
            
            self.render_cv(provider, **kwargs)
          

class ProviderEditAddressHandler(ProviderAdminBaseHandler):
    @admin_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        logging.info("provider dump before edit:" + str(vars(provider)))
        form = ProviderAddressForm(obj=provider)
        self.render_address(provider, address_form=form)

    # admin_required
    def post(self, vanity_url=None):
        form = ProviderAddressForm(self.request.POST)
        
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            provider_key = db.storeProvider(provider, self.request.POST)
            provider = provider_key.get()

            self.render_address(provider, address_form=form, success_message=saved_message)
        else:
            # show validation error
            provider = db.get_provider_from_vanity_url(vanity_url)
            self.render_address(provider, address_form=form)


class ProviderAddressUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        logging.info("(ProviderAddressUploadHandler.post) Found provider: %s" % provider.email)
        
        uploadForm = ProviderPhotoForm(self.request.POST)
        upload_files = self.get_uploads(uploadForm.profilePhoto.name)[0]
        
        logging.info("(ProviderAddressUploadHandler.post) Uploaded blob key: %s " % upload_files.key())
        provider.profile_photo_blob_key = upload_files.key()
        provider.put()
        
        # redirect to address edit page        
        self.redirect('/admin/provider/address/%s' % provider.vanity_url) 

class ProviderAdministrationHandler(ProviderAdminBaseHandler):
    
    @admin_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        if users.is_current_user_admin():
            self.render_administration(self, provider)
        else:
            logging.info("Not Admin: Can't see provider administration page")
        

  
class ProviderStatusHandler(ProviderAdminBaseHandler):
    def post(self):
        provider = db.get_from_urlsafe_key(self.request.get('provider_key'))
        new_status = self.request.get('status')
        provider.status = new_status
        provider.put()
        success_message = 'status changed to %s' % new_status
        self.render_administration(self, provider, success_message=success_message)


class ProviderFeaturesHandler(ProviderAdminBaseHandler):
    def post(self, feature_switch=None, vanity_url=None):
        
        # validate features that can be switched
        if feature_switch in ['booking_enabled', 'address_enabled']:
            provider = db.get_provider_from_vanity_url(vanity_url)
            
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
            
            self.render_administration(self, provider, success_message=success_message)

        else:
            logging.error('Received unknown feature switch : %s' % feature_switch)


class ProviderNotesHandler(ProviderAdminBaseHandler):
    
    @admin_required
    def get(self, vanity_url=None, note_key=None, operation=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        if users.is_current_user_admin():
            self.render_notes(provider)
        else:
            logging.info("Not Admin: Can't see provider notes page")
            
    def post(self, vanity_url=None, note_key=None, operation=None):
        if users.is_current_user_admin():
            provider = db.get_provider_from_vanity_url(vanity_url)
            if not operation:
                logging.info('type %s' % self.request.get('note_type'))
                provider.add_note(self.request.get('body'), note_type=self.request.get('note_type'))
                self.render_notes(provider)
            elif operation == 'edit':
                # todo: VALIDATE FORM!!!
                db.store(note_key, self.request.POST)
            elif operation == 'delete':
                logging.error('delete operation on notes is not handled')
            else:
                logging.error('unknown operation on notes:%s' % operation)
            self.render_notes(provider) 
        else:
            logging.info("Not Admin: Can't see provider notes page")
            
