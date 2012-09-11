from handler.auth import provider_required
from handler.provider import ProviderBaseHandler
from forms.provider import ProviderAddressForm, ProviderVanityURLForm
import logging
from data import db
from util import saved_message

class ProviderEditAddressHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        logging.info("provider dump before edit:" + str(vars(provider)))
        address_form = ProviderAddressForm().get_form(obj=provider)
        vanity_url_form = ProviderVanityURLForm().get_form(obj=provider)

        self.render_address(provider, address_form=address_form, vanity_url_form=vanity_url_form)

    @provider_required
    def post(self, vanity_url=None):
        form = ProviderAddressForm().get_form(self.request.POST)
        
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            form.populate_obj(provider)
            provider.put()

            vanity_url_form = ProviderVanityURLForm().get_form(obj=provider)

            self.render_address(provider, address_form=form, vanity_url_form=vanity_url_form, success_message=saved_message)

            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Success")

        else:
            # show validation error
            provider = db.get_provider_from_vanity_url(vanity_url)
            vanity_url_form = ProviderVanityURLForm().get_form(obj=provider)

            self.render_address(provider, address_form=form, vanity_url_form=vanity_url_form)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Validation Error")



        


class ProviderChangeURLHandler(ProviderBaseHandler):
    @provider_required
    def post(self, vanity_url=None):
        form = ProviderVanityURLForm().get_form(self.request.POST)
        
        if form.validate():
            # Store Provider
            provider = db.get_provider_from_vanity_url(vanity_url)
            
            form.populate_obj(provider)
            
            provider.put()

            self.redirect('/provider/address/' + provider.vanity_url)

            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Success")

        else:
            # show validation error
            provider = db.get_provider_from_vanity_url(vanity_url)
            address_form = ProviderAddressForm().get_form(obj=provider)

            self.render_address(provider, address_form=address_form, vanity_url_form=form)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit Address: Validation Error")


