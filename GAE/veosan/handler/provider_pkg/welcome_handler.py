from handler.auth import provider_required
from forms.provider import ProviderProfileForm
from handler.provider import ProviderBaseHandler
from data import db
from webapp2_extras.i18n import lazy_gettext as _



class ProviderMessageHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None, msg_key=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        
        messages = { 'new' : _("Welcome to Veosan! Please get started by completing your profile."),
                     'reset' : _("Welcome back! Password has been reset."),
                    }
        
        profile_form = ProviderProfileForm().get_form(obj=provider)
        self.render_profile(provider, profile_form=profile_form, success_message=messages[msg_key])
        

class WelcomeHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None, disable=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        if self.session.has_key('signup_button'):
            signup_origin = self.session['signup_button']
            if signup_origin:
                provider.signup_origin = signup_origin
                provider.put_async()

        if disable == 'disable':
            provider.display_welcome_page = False
            provider.put()
            self.redirect('/provider/profile/' + provider.vanity_url)
            return # don't render template after redirect

        self.render_template("provider/welcome.html", provider=provider)



