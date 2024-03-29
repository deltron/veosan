
import webapp2
import datetime
import mail
import logging
import re
from webapp2 import BaseRoute
from webapp2_extras.routes import PathPrefixRoute
from webapp2_extras import security
from webapp2_extras.i18n import lazy_gettext as _
from unidecode import unidecode

from data.model import Patient, PartialProvider
from data import db
from data.model_pkg.network_model import ProviderNetworkConnection
from data.model_pkg.provider_model import Provider
import forms
import handler
from handler.user_pkg.user_base_handler import UserBaseHandler


############################
# Signup
############################

class ProviderSignupHandler1(UserBaseHandler):
    def get(self, button = None):
        if button:
            site_counter = db.get_site_counter()
            if button == 'full':
                site_counter.click_full_button += 1
                self.session['signup_button'] = 'full'
                
            if button == 'preview':
                site_counter.click_preview_button += 1
                self.session['signup_button'] = 'preview'

            site_counter.put()

        provider_signup_form = forms.user.ProviderSignupForm1().get_form()
        
        self.render_template('user/signup_provider_1.html', provider_signup_form=provider_signup_form)      

    def post(self):
        provider_signup_form = forms.user.ProviderSignupForm1().get_form(self.request.POST)

        if provider_signup_form.validate():
            # save a partial provider in case they never finish
            partial_provider = PartialProvider()
            provider_signup_form.populate_obj(partial_provider)

            # set location info from request
            if "X-AppEngine-Country" in self.request.headers:
                partial_provider.gae_country = self.request.headers["X-AppEngine-Country"]
                
            if "X-AppEngine-Region" in self.request.headers:
                partial_provider.gae_region = self.request.headers["X-AppEngine-Region"]

            if "X-AppEngine-City" in self.request.headers:
                partial_provider.gae_city = self.request.headers["X-AppEngine-City"]
            
            if "X-AppEngine-CityLatLong" in self.request.headers:
                partial_provider.gae_city_lat_long = self.request.headers["X-AppEngine-CityLatLong"]

            partial_provider.put()
            
            # populate second form from first one
            provider_signup_form2 = forms.user.ProviderSignupForm2().get_form(self.request.POST, request_webob=self.request)
            
            # check the agreement by default
            provider_signup_form2['terms_agreement'].data = True
            
            # on to the next step
            self.render_template('user/signup_provider_2.html', provider_signup_form2=provider_signup_form2)
        else:
            self.render_template('user/signup_provider_1.html', provider_signup_form=provider_signup_form)

class ProviderSignupHandler2(UserBaseHandler):
    def get(self, prospect_id = None):
        # set prospect
        if prospect_id:
            self.log_prospect(prospect_id)
            prospect = db.get_prospect_from_prospect_id(prospect_id)
            
            # check if the prospect actually signed up
            if prospect:
                provider = db.get_provider_from_email(prospect.email)
                
                if provider:
                    language = prospect.language
                    redirect_url = "/" + language + "/signup/provider"
                    self.redirect(str(redirect_url))
                else:
                    # populate form with prospect info
                    provider_signup_form2 = forms.user.ProviderSignupForm2().get_form(obj=prospect, request_webob=self.request)
                    
                    # check the agreement by default
                    provider_signup_form2['terms_agreement'].data = True
                    
                    # on to the next step
                    self.render_template('user/signup_provider_2.html', provider_signup_form2=provider_signup_form2)
            else:
                self.redirect('/en/signup/provider')
        else:
            self.redirect('/en/signup/provider')
    
    def post(self):
        provider_signup_form2 = forms.user.ProviderSignupForm2().get_form(self.request.POST, request_webob=self.request)
        
        
        # check for double submit
        # if the first submit worked, a user should have been created and logged in
        user = self.get_current_user()
        if user:
            provider = db.get_provider_from_user(user)
            if provider:
                email = provider_signup_form2['email'].data
                if email == provider.email == user.get_email():
                    # someone is already logged in with the address being submitted
                    # probably a double submit...
                    self.redirect('/provider/welcome/' + provider.vanity_url)
                    return
        
        if provider_signup_form2.validate():            
            # init the provider
            provider = Provider()
            provider_signup_form2.populate_obj(provider)
            
            # pre-populate vanity_url with first name + last name + number if collision
            first_name = provider.first_name
            last_name = provider.last_name
            vanity_url = first_name + last_name

            provider.vanity_url = validate_vanity_url(vanity_url)
            
            provider.domain = self.get_domain()    
            
            
            # set location info from request
            if "X-AppEngine-Country" in self.request.headers:
                provider.gae_country = self.request.headers["X-AppEngine-Country"]
                
            if "X-AppEngine-Region" in self.request.headers:
                provider.gae_region = self.request.headers["X-AppEngine-Region"]

            if "X-AppEngine-City" in self.request.headers:
                provider.gae_city = self.request.headers["X-AppEngine-City"]
            
            if "X-AppEngine-CityLatLong" in self.request.headers:
                provider.gae_city_lat_long = self.request.headers["X-AppEngine-CityLatLong"]

            # save provider
            provider.put()
            
            # check if an invitation was associated to this
            invite = db.get_invite_from_email(provider.email)
            if invite:
                invite.profile_created = True
                invite.token = None
                invite.put()
                
                # connect this provider to invite_provider
                provider_network_connection = ProviderNetworkConnection()
                provider_network_connection.invite = invite.key
                provider_network_connection.source_provider = invite.provider
                provider_network_connection.target_provider = provider.key
                provider_network_connection.confirmed = True
            
                provider_network_connection.put()

            
            # now create an empty user for the provider
            user = self.create_empty_user_for_provider(provider)
            user.language = self.get_language()
            user.last_login = datetime.datetime.now()
            provider.profile_language = user.language
            provider.put()
            
            # set the password for the user
            password = provider_signup_form2.password.data
            password_hash = security.generate_password_hash(password, length=12)    
            user.password = password_hash
            user.put()
            
            # login with new password
            self.login_user(user.get_email(), password)

            # new user
            logging.info('(PasswordHandler.post) New user just set their password: %s' % user.get_email())
                
            self.redirect('/provider/welcome/' + provider.vanity_url)
                    
            self.log_event(user, "New account created for user")            # create a signup token for new user
                                    
            # remove partial provider
            partial_provider = db.get_partial_provider_from_email(provider.email)
            if partial_provider:
                partial_provider.key.delete()
                
            # Send welcome email to provider
            welcome_email_enabled = db.get_site_config().welcome_email_enabled
            if welcome_email_enabled:
                mail.email_provider_welcome(self.jinja2, provider)
            
            
        else:
            self.render_template('user/signup_provider_2.html', provider_signup_form2=provider_signup_form2)
            

class PatientSignupHandler(UserBaseHandler):
    def get(self):
        patient_signup_form = forms.user.PatientSignupForm().get_form()
        
        self.render_template('/user/signup_patient.html', patient_signup_form=patient_signup_form)      

    def post(self):
        patient_signup_form = forms.user.PatientSignupForm().get_form(self.request.POST)
        
        if patient_signup_form.validate():
            
            # init the patient
            patient = Patient()
            patient_signup_form.populate_obj(patient)
            patient.put()
            
            msg = _('Thanks for your interest. We will be in touch soon!')
            self.render_template('user/signup_patient.html', success_message=msg, patient_signup_form=patient_signup_form)
        else:
            self.render_template('user/signup_patient.html', patient_signup_form=patient_signup_form)


def validate_vanity_url(vanity_url):
    vanity_url = vanity_url.lower()
    
    # remove any non-alpha
    vanity_url = ''.join([c for c in vanity_url if c.isalpha()])
    
    # remove any unicode accents
    vanity_url = unidecode(vanity_url)
    
    # check if it's taken
    increment = 0
    while db.get_provider_from_vanity_url(vanity_url) is not None:
        increment += 1
        
        # strip previous number
        vanity_url = ''.join([c for c in vanity_url if c.isalpha()])
        
        # add a new number
        vanity_url = vanity_url + str(increment)
    
    
    # check if it's a reserved word
    route_list = webapp2.get_app().router.match_routes
    regex_to_check = []
    for route in route_list:
        if isinstance(route, BaseRoute):
            regex_to_check.append(route.template)
        elif isinstance(route, PathPrefixRoute):
            regex_to_check.append(route.prefix)


    reserved_url = False
    for regex in regex_to_check:
        # skip the default "/" route
        if not regex == "/":
            # remove leading slash
            regex = regex.replace("/", "", 1)
            # remove anything after trailing slash
            regex = regex.split("/")[0]
            
            if re.match(regex, vanity_url):
                reserved_url = True
        
    if reserved_url:
        increment += 1
        
        # strip previous number
        vanity_url = ''.join([c for c in vanity_url if c.isalpha()])
        
        # add a new number
        vanity_url = vanity_url + str(increment)
    
    return vanity_url
    
    