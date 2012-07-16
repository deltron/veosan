# -*- coding: utf-8 -*-
import logging
# GAE
from google.appengine.api import users
# veo
from base import BaseHandler
import data.db as db
from forms.provider import ProviderAddressForm, ProviderPhotoForm, ProviderNoteForm, ProviderStatusForm
from handler.auth import admin_required
from util import saved_message

class ProviderAdminBaseHandler(BaseHandler):
    
    def render_address(self, provider, address_form, **kw):
        self.render_template('provider/address.html', provider=provider, form=address_form, **kw)
    
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
            
