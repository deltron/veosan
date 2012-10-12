import logging, urlparse

# GAE
from webapp2_extras.i18n import gettext as _

# veo
import data.db as db
from forms.user import PasswordForm, LoginForm, ProviderSignupForm1
import mail
from google.appengine.ext import ndb
import datetime
from handler.base import BaseHandler

class UserBaseHandler(BaseHandler):           
    def render_login(self, next_action=None, key=None, **kw):
        login_form = LoginForm().get_form()
        
        if next_action == 'accept':
            if key:
                # get the source provider
                provider_network_connection = ndb.Key(urlsafe = key).get()
                
                # get the target provider (ie. the guy clicking the email)
                target_provider = provider_network_connection.target_provider.get()
                login_form = LoginForm().get_form(obj=target_provider)
                
        if next_action == 'booking':
            if key:
                # get the patient's email
                booking = ndb.Key(urlsafe = key).get()
                patient_from_booking = booking.patient.get()
                
                login_form = LoginForm().get_form(obj=patient_from_booking)

        login_form['remember_me'].data = True
        self.render_template('user/login.html', login_form=login_form, next_action=next_action, key=key, **kw)


class InviteHandler(UserBaseHandler):
    def get(self, invite_token=None):
        invite = db.get_invite_from_token(invite_token)
        if invite:
            invite_provider = invite.provider.get()
            
            # update invite status
            invite.link_clicked = True
            invite.put()
            
            logging.info("(InviteHandler.get) Invite token for %s from %s " % (invite.email, invite_provider.vanity_url))
    
            provider_signup_form = ProviderSignupForm1().get_form()
            provider_signup_form['email'].data = invite.email
            provider_signup_form['first_name'].data = invite.first_name
            provider_signup_form['last_name'].data = invite.last_name
    
            self.render_template('user/signup_provider_1.html', provider_signup_form=provider_signup_form)
        else:
            self.redirect("/login")    








