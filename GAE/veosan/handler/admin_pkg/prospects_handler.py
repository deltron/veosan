from handler.auth import admin_required
from handler.admin import AdminBaseHandler
import forms
from data.model_pkg.prospect_model import ProviderProspect
from data import db

class AdminProspectsHandler(AdminBaseHandler):
    @admin_required
    def get(self):
        prospects = db.fetch_provider_prospects()
        prospect_form = forms.provider.ProviderProspectForm().get_form()
        prospect_trio_form = forms.provider.ProviderProspectForm().get_form()

        self.render_template('admin/admin_prospects.html', prospects=prospects, prospect_form=prospect_form, prospect_trio_form=prospect_trio_form)

    def post(self):
        add_prospect_form = forms.provider.ProviderProspectForm().get_form(self.request.POST)
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
    def get(self, prospect_id = None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        if prospect:
            prospect.key.delete()
        
        self.redirect('/admin/prospects')


class AdminProspectDetailsHandler(AdminBaseHandler):
    @admin_required
    def get(self, prospect_id = None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)

        
        self.render_template('admin/prospect_details.html', prospect=prospect)
