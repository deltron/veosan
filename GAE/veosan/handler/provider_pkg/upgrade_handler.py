from handler.auth import provider_required
from handler.provider import ProviderBaseHandler
from data import db
import stripe
from data.model_pkg.provider_model import ProviderAccount
from stripe import CardError
import util

_STRIPE_TEST_KEY_SECRET = "sk_0CGm5DhYaiuarjtM4adlmooPeclET"
_STRIPE_PROD_KEY_SECRET = "sk_0CGm0CBZ8jbZX5N1W1hJ9vH36tDff"

_STRIPE_TEST_KEY_PUBLIC = 'pk_0CGm7P3z0UJVLSfX3Pj5z7NKuzUjj'
_STRIPE_PROD_KEY_PUBLIC = "pk_0CGmD1EM1Gz1vUdFrUl2WSP3Xep9a"


class ProviderUpgradeHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        stripe_key = _STRIPE_TEST_KEY_PUBLIC
        if util.is_dev_server(self.request):
            stripe_key = _STRIPE_TEST_KEY_PUBLIC
        else:
            stripe_key = _STRIPE_PROD_KEY_PUBLIC

        self.render_template("provider/upgrade.html", provider=provider, stripe_key=stripe_key)

    @provider_required
    def post(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)

        # set your secret key: remember to change this to your live secret key in production
        # see your keys here https://manage.stripe.com/account
        if util.is_dev_server(self.request):
            stripe.api_key = _STRIPE_TEST_KEY_SECRET
        else:
            stripe.api_key = _STRIPE_PROD_KEY_SECRET
        
        # get the credit card details submitted by the form
        token = self.request.POST['stripeToken']
        plan = self.request.POST['plan']

        try :
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
            provider.upgrade_enabled = False

            provider.put()
            
            self.redirect("/provider/upgrade/success/" + provider.vanity_url)
        except CardError:
            self.render_template("provider/upgrade_failed.html", provider=provider)


class ProviderUpgradeSuccessHandler(ProviderBaseHandler):
    @provider_required
    def get(self, vanity_url=None):
        provider = db.get_provider_from_vanity_url(vanity_url)        
        self.render_template("provider/upgrade_success.html", provider=provider)

