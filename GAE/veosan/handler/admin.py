'''
    admin handlers
'''

import logging

# veo
from base import BaseHandler
import data.db as db
import util
from handler.auth import admin_required
from data.model import SiteLog
from data.model_pkg.provider_model import Provider
import forms
from data.model_pkg.prospect_model import ProviderProspect



class AdminBaseHandler(BaseHandler):
    ''' Base functions for administration pages''' 

    def render_providers(self, **kw):
        providers = db.fetch_providers()
        self.render_template('admin/admin_providers.html', providers=providers, **kw)

    def render_data(self, **kw):
        dev_server = util.is_dev_server(self.request)
        site_config = db.get_site_config()
        
        logging.info('(AdminBaseHandler.render_data) dev_server=%s' % dev_server)
        self.render_template('admin/data.html', dev_server=dev_server, site_config=site_config, **kw)

class AdminIndexHandler(AdminBaseHandler):
    '''Administration Index'''

    @admin_required
    def get(self):
        # kick out any logged in users
        user = self.get_current_user()
        if user:
            logging.info("(LogoutHandler.get) Logging out user %s because admin logged in" % user.get_email())
            
            # log the event
            self.log_event(user, "Logged out by admin")

        self.auth.unset_session()
        
        self.redirect('/admin/dashboard')


class AdminSiteConfigHandler(AdminBaseHandler):
    def post(self, feature=None):
        
        # validate features that can be switched
        if feature in ['booking_enabled', 'google_analytics_enabled', 'facebook_like_enabled', 'signup_enabled', 'error_email_enabled']:            
            site_config = db.get_site_config()

            # toggle state
            current_state = getattr(site_config, feature)
            
            if current_state:           
                setattr(site_config, feature, False)
                success_message = 'feature %s is now set to %s' % (feature, False)
                    
            else:
                setattr(site_config, feature, True)
                success_message = 'feature %s is now set to %s' % (feature, True)

            site_config.put()
            
            self.render_data(success_message=success_message)

        else:
            logging.error('Received unknown feature switch : %s' % feature)




class AdminProvidersHandler(AdminBaseHandler):
    ''' Administer Providers '''
 
    @admin_required
    def get(self):
        self.render_providers()
        
class AdminPatientsHandler(AdminBaseHandler):
    ''' Administer Patients '''
 
    @admin_required
    def get(self):
        patients = db.fetch_patients()
        self.render_template('admin/patients.html', patients=patients)

class AdminInvitesHandler(AdminBaseHandler):
    ''' Administer Invitations '''
 
    @admin_required
    def get(self):
        invites = db.fetch_invites()
        self.render_template('admin/invites.html', invites=invites)

        
class AdminDashboardHandler(AdminBaseHandler):
    @admin_required
    def get(self):
        stats_map = {}

        # get hits to any page
        stats_map['page_hit_count'] = SiteLog.query(SiteLog.page == '/', SiteLog.admin_email == None).count()
      
        # get hits to home page
        stats_map['homepage_hit_count'] = SiteLog.query(SiteLog.page == '/', SiteLog.admin_email == None).count()

        # get hits to provider signup page
        stats_map['provider_signup_hit_count'] = SiteLog.query(SiteLog.page == '/signup/provider', SiteLog.admin_email == None).count()

        # get total # of providers
        stats_map['provider_total_count'] = Provider.query().count()

        # get hits from Internet Explorer
        stats_map['internet_explorer_count'] = db.get_site_counter().internet_explorer_hits

        # number of times exiting site to blog
        stats_map['blog_clicks'] = db.get_site_counter().blog_clicks
        
        self.render_template('admin/dashboard.html', stats_map=stats_map)


class AdminProspectsHandler(AdminBaseHandler):
    @admin_required
    def get(self):
        prospects = db.fetch_provider_prospects()
        prospect_form = forms.provider.ProviderProspectForm().get_form()
        self.render_template('admin/admin_prospects.html', prospects=prospects, prospect_form=prospect_form)

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

