from handler.auth import provider_required
from handler.provider import ProviderBaseHandler
from data import db
from google.appengine.ext import ndb
from forms.provider import ProviderInviteForm
import urlparse
import logging
import mail
from handler import auth
from data.model_pkg.network_model import ProviderNetworkConnection, Invite
from webapp2_extras.i18n import lazy_gettext as _

class ProviderNetworkHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None, operation=None, provider_key=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        error_message = None
        success_message = None
        
        if operation == 'accept':
            provider_network_connection = ndb.Key(urlsafe=provider_key).get()
            source_provider_key = provider_network_connection.source_provider
            source_provider = source_provider_key.get()
            
            if provider_network_connection.confirmed:

                # already connected
                msg = _('You are already connected to')
                success_message = msg + " %s %s" % (source_provider.first_name, source_provider.last_name)
            else:
                target_provider_key = provider.key
                
                if source_provider_key == target_provider_key:
                    success_message = _("You can't connect to yourself!")
                
                else:
                    provider_network_connection = db.get_provider_network_connection(source_provider_key, target_provider_key)
                    if provider_network_connection:
                        provider_network_connection.confirmed = True
                        provider_network_connection.rejected = False
                        
                        try:
                            provider_network_connection.put()
                            msg = _('You are now connected to')
                            success_message = msg + " %s %s" % (source_provider.first_name, source_provider.last_name)
                        except Exception as e:
                            error_message = 'Error making connection: ' + e.message
                    else:
                        error_message = _('No connection found')
                
        if operation == 'reject':
            provider_network_connection = ndb.Key(urlsafe=provider_key).get()
            source_provider_key = provider_network_connection.source_provider
            source_provider = source_provider_key.get()
            target_provider_key = provider.key
            
            # keep the connection around just mark it as rejected
            provider_network_connection = db.get_provider_network_connection(source_provider_key, target_provider_key)
            provider_network_connection.rejected = True
            provider_network_connection.rejection_count += 1
            provider_network_connection.put()
            
            msg = _("You have rejected")
            success_message = msg + " %s %s" % (source_provider.first_name, source_provider.last_name)
        
        provider_invite_form = ProviderInviteForm().get_form()
        
        self.render_template("provider/network.html", provider=provider, provider_invite_form=provider_invite_form, success_message=success_message, error_message=error_message)

    @provider_required
    def post(self, vanity_url=None, operation=None, provider_key=None):
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
                msg = "Invitation sent to"
                message = msg + " %s %s" % (invite.first_name, invite.last_name)
                
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
            
            # check if there is already a pending request
            
            if provider_source in provider_target.get_provider_network_pending():
                message = "Connection pending..."
                self.render_public_profile(provider=provider_target, success_message=message)
            elif provider_source in provider_target.get_provider_network():
                message = "Already connected!"
                self.render_public_profile(provider=provider_target, success_message=message)
            elif provider_source == provider_target:
                message = "You can't connect to yourself!"
                self.render_public_profile(provider=provider_target, success_message=message)
            else:
                provider_network_connection = None
                
                if provider_source in provider_target.get_provider_network_rejected():
                    # this connection was rejected before.
                    provider_network_connection = db.get_provider_network_connection(provider_source.key, provider_target.key)
                    # what the hell...let them try again!
                    provider_network_connection.rejected = False
                else:
                    # no pending request, let's make one        
                    provider_network_connection = ProviderNetworkConnection()
                    provider_network_connection.source_provider = provider_source.key
                    provider_network_connection.target_provider = provider_target.key
                    
                provider_network_connection.confirmed = False

                try:
                    provider_network_connection.put()

                    message = "Connection requested"
                    self.render_public_profile(provider=provider_target, success_message=message)
                    
                    # now send out an email
                    # the url for accepting for target_provider
                    url_obj = urlparse.urlparse(self.request.url)
                    accept_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/login/accept/' + provider_network_connection.key.urlsafe(), '', '', ''))
                        
                    mail.email_connect_request(self.jinja2, from_provider=provider_source, target_provider=provider_target, accept_url=accept_url)
                    
                except Exception as e:
                    error_message = 'Error making connection: ' + e.message
                    self.render_public_profile(provider=provider_target, error_message=error_message)

                    
        else:
            # redirect to login page if not logged in, then send back here after creditials are verified
            self.redirect("/login/connect/" + provider_target.key.urlsafe())
        
        
