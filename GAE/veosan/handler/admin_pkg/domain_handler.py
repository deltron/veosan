from handler.admin import AdminBaseHandler
import util
import logging
from google.appengine.ext import ndb
from handler.auth import admin_required
from data import db
from forms.admin import DomainSetupForm
from data.model_pkg.site_model import DomainSetup

class DomainSetupHandler(AdminBaseHandler):
    @admin_required
    def get(self, domain = None):
        if not domain:
            self.render_template('admin/domain-setup.html', domain_list = util.DOMAINS)
        else:
            domain_setup = db.get_domain_setup(domain)
            if not domain_setup:
                domain_setup = DomainSetup()
                domain_setup.domain_name = domain
                domain_setup.put()
                
            domain_setup_form = DomainSetupForm().get_form(obj=domain_setup)
            
            self.render_template('admin/domain-setup.html', domain=domain, form=domain_setup_form)
        
    def post(self, domain = None):
        form = DomainSetupForm().get_form(self.request.POST)
        
        if form.validate():
            domain_setup = db.get_domain_setup(domain)
            
            form.populate_obj(domain_setup)
            domain_setup.put()
            
            self.redirect('/admin/domain/' + domain)
        else:
            self.render_template('admin/domain-setup.html', domain=domain, form=form)
