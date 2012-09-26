from handler.auth import provider_required
from forms.provider import ProviderProfileForm
from handler.provider import ProviderBaseHandler
from data import db
from webapp2_extras.i18n import lazy_gettext as _
import stripe
from data.model_pkg.provider_model import ProviderAccount


class ProviderUpgradeHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        self.render_template("provider/upgrade.html", provider=provider)

    @provider_required
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        # set your secret key: remember to change this to your live secret key in production
        # see your keys here https://manage.stripe.com/account
        stripe.api_key = "sk_0CGm5DhYaiuarjtM4adlmooPeclET"
        
        # get the credit card details submitted by the form
        token = self.request.POST['stripeToken']
        plan = self.request.POST['plan']

        customer = stripe.Customer.create(
            card=token,
            plan=plan,
            email=provider.email
        )

        # save the customer ID in your database so you can use it later
        provider_account = ProviderAccount()
        provider_account.provider = provider.key
        provider_account.stripe_customer_id = customer.id
        provider_account.stripe_plan_id = plan
        provider_account.put()
        
        provider.booking_enabled = True
        provider.put()
        
        self.render_template("provider/upgrade_success.html", provider=provider)



