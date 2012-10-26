# -*- coding: utf-8 -*-
import logging
# GAE
from google.appengine.api import users
from webapp2_extras import security 

# veo
from base import BaseHandler
import data.db as db
from handler.auth import admin_required
from data.model_pkg.network_model import ProviderNetworkConnection
import urlparse
from forms.provider import ProviderDomainForm

class ProviderAdminBaseHandler(BaseHandler):
    @staticmethod
    def render_administration(handler, provider, **kw):
        user_from_provider = db.get_user_from_email(provider.email)
        
        domain_form = ProviderDomainForm().get_form(obj=provider)
        
        handler.render_template('provider/administration.html', provider=provider, user_from_provider=user_from_provider, domain_form=domain_form, **kw)
    
     

class ProviderAdministrationHandler(ProviderAdminBaseHandler):
    @admin_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        if users.is_current_user_admin():
            self.render_administration(self, provider)
        else:
            logging.info("Not Admin: Can't see provider administration page")
        

  
class ProviderDomainSetupHandler(ProviderAdminBaseHandler):
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        domain_form = ProviderDomainForm().get_form(self.request.POST)
        if domain_form.validate():
            domain_form.populate_obj(provider)
            provider.put()
            
        self.render_administration(self, provider)


class ProviderFeaturesHandler(ProviderAdminBaseHandler):
    def get(self, feature_switch=None, vanity_url=None):
        
        # validate features that can be switched
        if feature_switch in ['booking_enabled', 'address_enabled', 'connect_enabled', 'stats_enabled', 'upgrade_enabled']:
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            # toggle state
            current_state = getattr(provider, feature_switch)
            
            if current_state:           
                setattr(provider, feature_switch, False)
                success_message = 'feature %s is now set to %s' % (feature_switch, False)
                #provider.add_note('%s = False' % feature_switch)
                    
            else:
                setattr(provider, feature_switch, True)
                success_message = 'feature %s is now set to %s' % (feature_switch, True)
                #provider.add_note('%s = True' % feature_switch)

            provider.put()
            
            self.render_administration(self, provider, success_message=success_message)

        else:
            logging.error('Received unknown feature switch : %s' % feature_switch)


class ProviderDomainHandler(ProviderAdminBaseHandler):
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        provider.vanity_domain = self.request.get('domain')
        provider.put()
        
        logging.info("(ProviderDomainHandler) Provider %s setting vanity domain to %s" % (provider.email, provider.vanity_domain))

        self.redirect('/admin/provider/admin/' + provider.vanity_url)

class ProviderForceFriendsHandler(ProviderAdminBaseHandler):
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        target_provider_email = self.request.get('email')
        if target_provider_email:
            target_provider = db.get_provider_from_email(target_provider_email)
            
            provider_network_connection = ProviderNetworkConnection()
            provider_network_connection.source_provider = provider.key
            provider_network_connection.target_provider = target_provider.key
            provider_network_connection.confirmed = True
            provider_network_connection.rejected = False
            provider_network_connection.forced_by_admin = True
            provider_network_connection.put()

            logging.info("(ProviderForceFriendsHandler) Provider %s forcing connection to %s" % (provider.email, provider.vanity_domain))

        self.redirect('/admin/provider/admin/' + provider.vanity_url)

class ProviderChangePasswordHandler(ProviderAdminBaseHandler):
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        new_password = self.request.get('password')
        if provider and new_password:
            user = db.get_user_from_email(provider.email)
            if user:
                # hash password (same as passing password_raw to user_create)
                password_hash = security.generate_password_hash(new_password, length=12)    
                user.password = password_hash
                user.put()
                
        self.redirect('/admin/provider/admin/' + provider.vanity_url)

class ProviderGenerateClaimHandler(ProviderAdminBaseHandler):
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        user = db.get_user_from_email(provider.email)
        token = self.create_token(user, 'set_new_password')
        
        # claim url
        url_obj = urlparse.urlparse(self.request.url)
        claim_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/claim/' + token, '', '', ''))
        
        user.claim_url = claim_url
        user.put()

        self.redirect('/admin/provider/admin/' + provider.vanity_url)



class ProviderEventLogHandler(ProviderAdminBaseHandler):
    @admin_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        user = provider.user.get()
        
        events = db.get_events_for_user(user)
        
        self.render_template("/provider/event_log.html", provider=provider, events=events)


