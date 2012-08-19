
from handler.user import UserBaseHandler
from forms.user import ProviderSignupForm1, ProviderSignupForm2,\
    PatientSignupForm
import util
from data.model import Provider, ProviderNetworkConnection, Patient
from unidecode import unidecode
from data import db, search_index
import webapp2
from webapp2 import BaseRoute
from webapp2_extras.routes import PathPrefixRoute
from webapp2_extras import security
import logging
import re

############################
# Signup
############################

class ProviderSignupHandler1(UserBaseHandler):
    def get(self, lang_key=None):
        if lang_key and lang_key in util.LANGUAGES:
            self.set_language(lang_key)
            self.redirect('/signup/provider')            

        provider_signup_form = ProviderSignupForm1().get_form()
        
        self.render_template('user/signup_provider_1.html', provider_signup_form=provider_signup_form)      

    def post(self, lang_key=None):
        provider_signup_form = ProviderSignupForm1().get_form(self.request.POST)

        if provider_signup_form.validate():
            # populate second form from first one
            provider_signup_form2 = ProviderSignupForm2().get_form(self.request.POST)
            
            # check the agreement by default
            provider_signup_form2['terms_agreement'].data = True
            
            # on to the next step
            self.render_template('user/signup_provider_2.html', provider_signup_form2=provider_signup_form2)
        else:
            self.render_template('user/signup_provider_1.html', provider_signup_form=provider_signup_form)

class ProviderSignupHandler2(UserBaseHandler):
    def post(self, lang_key=None):
        provider_signup_form2 = ProviderSignupForm2().get_form(self.request.POST)
        
        if provider_signup_form2.validate():            
            # init the provider
            provider = Provider()
            provider_signup_form2.populate_obj(provider)
            
            # pre-populate vanity_url with first name + last name + number if collision
            first_name_first_letter = provider.first_name
            last_name = provider.last_name
            
            vanity_url = first_name_first_letter + last_name
            vanity_url = vanity_url.lower()
            
            # remove any non-alpha
            vanity_url = ''.join([c for c in vanity_url if c.isalpha()])
            
            # remove any unicode accents
            vanity_url = unidecode(vanity_url)
            
            # check if it's taken
            increment = 0
            while db.get_provider_from_vanity_url(vanity_url) is not None:
                increment = increment + 1
                
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
                # remove leading slash
                regex = regex.replace("/", "", 1)
                # remove anything after trailing slash
                regex = regex.split("/")[0]
                
                if re.match(regex, vanity_url):
                    reserved_url = True
            
            if reserved_url:
                increment = increment + 1
                
                # strip previous number
                vanity_url = ''.join([c for c in vanity_url if c.isalpha()])
                
                # add a new number
                vanity_url = vanity_url + str(increment)
            
            
            
            provider.vanity_url = vanity_url           
            
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
                        
            # update the index
            search_index.IndexProvider(provider)
        else:
            self.render_template('user/signup_provider_2.html', provider_signup_form2=provider_signup_form2)
            

class PatientSignupHandler(UserBaseHandler):
    def get(self, lang_key=None):
        if lang_key and lang_key in util.LANGUAGES:
            self.set_language(lang_key)
            self.redirect('/signup/patient')            

        patient_signup_form = PatientSignupForm().get_form()
        
        self.render_template('/user/signup_patient.html', patient_signup_form=patient_signup_form)      

    def post(self, lang_key=None):
        patient_signup_form = PatientSignupForm().get_form(self.request.POST)
        
        if patient_signup_form.validate():
            
            # init the patient
            patient = Patient()
            patient_signup_form.populate_obj(patient)
            patient.put()
            
            msg = _('Thanks for your interest. We will be in touch soon!')
            self.render_template('user/signup_patient.html', success_message=msg, patient_signup_form=patient_signup_form)
        else:
            self.render_template('user/signup_patient.html', patient_signup_form=patient_signup_form)
