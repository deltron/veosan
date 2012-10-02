from handler.auth import admin_required
from handler.admin import AdminBaseHandler
from data.model_pkg.prospect_model import ProviderProspect, ProspectNote
from data import db
import logging
from google.appengine.api import users
from google.appengine.ext import ndb
from forms.prospect_forms import ProviderProspectForm, ProspectNoteForm, \
     ProspectTagsForm, ProspectEmploymentTagsForm, ProspectAddToCampaignForm

class AdminProspectsHandler(AdminBaseHandler):
    @admin_required
    def get(self):
        cursor_key = self.request.get('cursor', None)
        prospects, next_curs, prev_curs = db.fetch_page_of_provider_prospects(cursor_key=cursor_key)
        prospect_form = ProviderProspectForm().get_form()
        self.render_template('admin/admin_prospects.html', prospects=prospects, next_curs=next_curs, prev_curs=prev_curs, prospect_form=prospect_form)


    def post(self):
        add_prospect_form = ProviderProspectForm().get_form(self.request.POST)
        prospects = db.fetch_page_of_provider_prospects()

        if add_prospect_form.validate():
            provider_prospect = ProviderProspect()
            add_prospect_form.populate_obj(provider_prospect)
            provider_prospect.put()
            self.redirect("/admin/prospects")
        else:
            self.render_template('admin/admin_prospects.html', prospects=prospects, prospect_form=add_prospect_form)
    



class AdminProspectDeleteHandler(AdminBaseHandler):
    @admin_required
    def get(self, prospect_id=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        if prospect:
            prospect.key.delete()
        
        self.redirect('/admin/prospects')


class AdminProspectDetailsHandler(AdminBaseHandler):
    @admin_required
    def get(self, prospect_id=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)

        prospect_note_form = ProspectNoteForm().get_form()
        prospect_tags_form = ProspectTagsForm().get_form(obj=prospect)
        prospect_employment_tags_form = ProspectEmploymentTagsForm().get_form(obj=prospect)
        add_to_campaign_form = ProspectAddToCampaignForm().get_form()

        self.render_template('admin/prospect_details.html', prospect=prospect, 
                             prospect_note_form=prospect_note_form, prospect_tags_form=prospect_tags_form,
                             prospect_employment_tags_form=prospect_employment_tags_form, add_to_campaign_form=add_to_campaign_form)
        
        

class AdminProspectTagsHandler(AdminBaseHandler):
    def post(self, prospect_id=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        prospect_tags_form = ProspectTagsForm().get_form(self.request.POST)
        if prospect_tags_form.validate():
            if prospect_tags_form['tags'].data is None:
                prospect.tags = []
            else:
                prospect_tags_form.populate_obj(prospect)
                
            prospect.put()
            
            prospect_note = ProspectNote()
            prospect_note.prospect = prospect.key
            google_user = users.get_current_user()    
            prospect_note.user = google_user
            prospect_note.note_type = 'admin'
            
            prospect_tags_string = ""
            for tag in prospect.tags:
                prospect_tags_string += tag + ', '
            
            # chop the last comma
            prospect_tags_string = prospect_tags_string[:-2]
            # escape underscores for markdown
            prospect_tags_string = prospect_tags_string.replace('_', '\_')
            
            if not prospect_tags_string:
                prospect_note.body = "Deleted tags"
            else:
                prospect_note.body = 'Updated tags to: ' + prospect_tags_string
                
            prospect_note.put()

            
            self.redirect('/admin/prospects/' + prospect.prospect_id)

class AdminProspectEmploymentTagsHandler(AdminBaseHandler):
    def post(self, prospect_id=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        prospect_employment_tags_form = ProspectEmploymentTagsForm().get_form(self.request.POST)
        if prospect_employment_tags_form.validate():
            if prospect_employment_tags_form['employment_tags'].data is None:
                prospect.employment_tags = []
            else:
                prospect_employment_tags_form.populate_obj(prospect)
                
            prospect.put()
            
            prospect_note = ProspectNote()
            prospect_note.prospect = prospect.key
            google_user = users.get_current_user()    
            prospect_note.user = google_user
            prospect_note.note_type = 'admin'
            
            prospect_tags_string = ""
            for tag in prospect.employment_tags:
                prospect_tags_string += tag + ', '
            
            # chop the last comma
            prospect_tags_string = prospect_tags_string[:-2]
            # escape underscores for markdown
            prospect_tags_string = prospect_tags_string.replace('_', '\_')

            if not prospect_tags_string:
                prospect_note.body = "Deleted employment tags"
            else:
                prospect_note.body = 'Updated employment tags to: ' + prospect_tags_string
                
            prospect_note.put()

            
            self.redirect('/admin/prospects/' + prospect.prospect_id)


class AdminProspectAddToCampaignHandler(AdminBaseHandler):
    
    def post(self, prospect_id=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        add_to_campaign_form = ProspectAddToCampaignForm().get_form(self.request.POST)
        if add_to_campaign_form.validate():
            campaign_urlsafe_key = add_to_campaign_form.campaign.data
            campaign = db.get_from_urlsafe_key(campaign_urlsafe_key)
            if prospect.key not in campaign.prospects:
                campaign.prospects.append(prospect.key)
                # TODO: create admin note
                campaign.put()
            else:
                error_message = 'Prospect is already a member of the campaign %s' % campaign.name
                logging.error(error_message)
            
        self.redirect('/admin/prospects/' + prospect.prospect_id) 


class AdminProspectNotesHandler(AdminBaseHandler):
    @admin_required
    def get(self, prospect_id=None, operation=None, key=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        note_key = ndb.Key(urlsafe=key)

        if prospect:
            if operation == 'delete':
                note_key.delete()
                self.redirect('/admin/prospects/' + prospect.prospect_id)
        
            if operation == 'edit':
                if note_key:
                    note = note_key.get()
                    prospect_note_form = ProspectNoteForm().get_form(obj=note)
                    prospect_tags_form = ProspectTagsForm().get_form(obj=prospect)
                    prospect_employment_tags_form = ProspectEmploymentTagsForm().get_form(obj=prospect)
                    add_to_campaign_form = ProspectAddToCampaignForm().get_form()
                    
                    self.render_template('admin/prospect_details.html', prospect=prospect,
                                         prospect_note_form=prospect_note_form,
                                         prospect_tags_form=prospect_tags_form,
                                         prospect_employment_tags_form=prospect_employment_tags_form,
                                         add_to_campaign_form = add_to_campaign_form,
                                         edit='note',
                                         edit_key=key)

    def post(self, prospect_id=None, operation=None, key=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        prospect_tags_form = ProspectTagsForm().get_form(obj=prospect)
        prospect_employment_tags_form = ProspectEmploymentTagsForm().get_form(obj=prospect)
        prospect_note_form = ProspectNoteForm().get_form(self.request.POST)
        add_to_campaign_form = ProspectAddToCampaignForm().get_form()
        
        if prospect_note_form.validate():
            prospect_note = None
            if operation == 'add':
                prospect_note = ProspectNote()
                
            if operation == 'edit':
                note_key = ndb.Key(urlsafe=key)
                prospect_note = note_key.get()
            
            prospect_note.prospect = prospect.key
            prospect_note_form.populate_obj(prospect_note)
            google_user = users.get_current_user()    
            prospect_note.user = google_user
            prospect_note.put()
            # re calculate notes stats
            prospect.calculate_notes_stats()

            self.redirect('/admin/prospects/' + prospect.prospect_id)

        
        else:
            self.render_template('admin/prospect_details.html',
                                 prospect=prospect,
                                 prospect_note_form=prospect_note_form,
                                 prospect_tags_form=prospect_tags_form,
                                 prospect_employment_tags_form=prospect_employment_tags_form,
                                 add_to_campaign_form = add_to_campaign_form)

        
