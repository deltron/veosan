from handler.auth import provider_required
from handler.provider import ProviderBaseHandler
from data import db
from google.appengine.ext import ndb
from forms.provider import ProviderInviteForm
from data.model import Invite, ProviderNetworkConnection
import urlparse
import logging
import mail
from handler import auth

class ProviderNetworkHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None, operation=None, provider_key = None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        error_message = None
        success_message = None
        
        if operation == 'accept':
            source_provider_key = ndb.Key(urlsafe=provider_key)
            source_provider = source_provider_key.get()
            target_provider_key = provider.key
            
            provider_network_connection = db.get_provider_network_connection(source_provider_key, target_provider_key)
            provider_network_connection.confirmed = True
            
            try:
                provider_network_connection.put()
            except Exception as e:
                error_message = 'Error making connection: ' + e
            
            success_message = "You are now connected to %s %s" % (source_provider.first_name, source_provider.last_name)
            
        if operation == 'reject':
            source_provider_key = ndb.Key(urlsafe=provider_key)
            source_provider = source_provider_key.get()
            target_provider_key = provider.key
                        
            provider_network_connection = db.get_provider_network_connection(source_provider_key, target_provider_key)
            provider_network_connection.key.delete()
            
            success_message = "You have rejected %s %s" % (source_provider.first_name, source_provider.last_name)
        
        provider_invite_form = ProviderInviteForm().get_form()
        
        self.render_template("provider/network.html", provider=provider, provider_invite_form=provider_invite_form, success_message=success_message, error_message=error_message)

    @provider_required
    def post(self, vanity_url=None, operation=None, provider_key = None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        if operation == 'invite' :
            form = ProviderInviteForm().get_form(self.request.POST)
            if form.validate():
                invite = Invite()
                form.populate_obj(invite)
                
                # associate provider to invite
                invite.provider = provider.key
                
                # create a token for this invite that will be used to pre-populate the signup form
                invite.token = self.create_token(invite.email)
                
                # save
                invite.put()
                
                # create an invite url
                url_obj = urlparse.urlparse(self.request.url)
                invite_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/invite/' + invite.token, '', '', ''))
                logging.info('(ProviderNetworkHandler.post) unique invite URL:' + invite_url)
    
                # send the actual email...
                mail.email_invite(self.jinja2, invite, invite_url)
                
                # all good
                message = "Invitation sent to %s %s (%s)" % (invite.first_name, invite.last_name, invite.email)
                
                # new form for next invite
                provider_invite_form = ProviderInviteForm().get_form()
                self.render_template("provider/network.html", success_message=message, provider=provider, provider_invite_form=provider_invite_form)
            else:
                self.render_template("provider/network.html", provider=provider, provider_invite_form=form)
        else:
            # post unknown operation
            
            provider_invite_form = ProviderInviteForm().get_form()
            self.render_template("provider/network.html", success_message=message, provider=provider, provider_invite_form=provider_invite_form)

class ProviderConnectHandler(ProviderBaseHandler):
    def get(self, vanity_url=None):
        provider_target = db.get_provider_from_vanity_url(vanity_url)
        
        user_source = self.get_current_user()
        if user_source and auth.PROVIDER_ROLE in user_source.roles:
            provider_source = db.get_provider_from_user(user_source)
            
            provider_network_connection = ProviderNetworkConnection()
            provider_network_connection.source_provider = provider_source.key
            provider_network_connection.target_provider = provider_target.key
            provider_network_connection.confirmed = False
            
            provider_network_connection.put()
            
            message = "Connection requested"
            self.render_public_profile(provider=provider_target, success_message=message)
        else:
            # redirect to login page if not logged in
            self.redirect("/login/connect/" + provider_target.key.urlsafe())
        
        