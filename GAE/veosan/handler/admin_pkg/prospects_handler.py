from handler.auth import admin_required
from handler.admin import AdminBaseHandler
from data.model_pkg.prospect_model import ProviderProspect, ProspectNote
from data import db
from google.appengine.api import users
from google.appengine.ext import ndb
from forms.prospect_forms import ProviderProspectForm, ProspectNoteForm,\
    ProspectStatusForm

class AdminProspectsHandler(AdminBaseHandler):
    @admin_required
    def get(self):
        prospects = db.fetch_provider_prospects()
        prospect_form = ProviderProspectForm().get_form()

        self.render_template('admin/admin_prospects.html', prospects=prospects, prospect_form=prospect_form)

    def post(self):
        add_prospect_form = ProviderProspectForm().get_form(self.request.POST)
        prospects = db.fetch_provider_prospects()

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
        prospect_status_form = ProspectStatusForm().get_form(obj=prospect)
        
        self.render_template('admin/prospect_details.html', prospect=prospect, prospect_note_form=prospect_note_form, prospect_status_form=prospect_status_form)

class AdminProspectStatusHandler(AdminBaseHandler):
    def post(self, prospect_id=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        prospect_status_form = ProspectStatusForm().get_form(self.request.POST)
        if prospect_status_form.validate():
            new_status = prospect_status_form['status'].data
            prospect.status = new_status 
            prospect.put()
            
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
                    prospect_status_form = ProspectStatusForm().get_form(obj=prospect)
                    
                    self.render_template('admin/prospect_details.html', prospect=prospect,
                                         prospect_note_form=prospect_note_form,
                                         prospect_status_form=prospect_status_form,
                                         edit='note',
                                         edit_key=key)

    def post(self, prospect_id=None, operation=None, key=None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        prospect_status_form = ProspectStatusForm().get_form(obj=prospect)
        prospect_note_form = ProspectNoteForm().get_form(self.request.POST)
        
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

            self.redirect('/admin/prospects/' + prospect.prospect_id)

        
        else:
            self.render_template('admin/prospect_details.html', prospect=prospect, prospect_note_form=prospect_note_form, prospect_status_form=prospect_status_form)

        
