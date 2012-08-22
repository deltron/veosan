import logging, sha, random
from google.appengine.api import users
import webapp2
from webapp2_extras import auth, i18n, jinja2, sessions

# veo
import data
import handler.auth
import util
from data import db
from data.model import SiteConfig, LogEvent, User, SiteLog
from google.appengine.ext.ndb.key import Key
from google.appengine.ext import ndb
import re

class BaseHandler(webapp2.RequestHandler):
    '''
        Base Handler for the whole site. Provides templating, user and authentication services
    '''
    
    # _translations = None
    
    @webapp2.cached_property
    def jinja2(self):
        '''
            jinja2 renderer
        '''
        j = jinja2.get_jinja2(app=self.app)
        return j

    def render_template(self, filename, provider=None, **kw):
        '''
            Common template rendering function
        '''
        
        # add template arguments common to all templates
        user = self.get_current_user()
        roles = []
        
        # hack for providers 
        # (allows provider pages to be accessed without a user logged in but knowing the provider key)
        kw['provider'] = provider
        kw['provider_from_user'] = None

        # somebody is logged in
        if user:
            logging.info('(BaseHandler.render_template) User logged in: %s with roles %s' % (user.get_email(), user.roles))
            kw['user'] = user
                        
            # extend roles
            roles.extend(user.roles)
            
            # is it a provider?
            if handler.auth.PROVIDER_ROLE in roles:
                provider_from_user = data.db.get_provider_from_user(user)
                logging.info('(BaseHandler.render_template) Provider logged in: ' + user.get_email())
                
                # overwrite for menu from logged in user
                kw['provider_from_user'] = provider_from_user


                # verify user->provider matches request->provider passed as paramater (ie. from request key)
                if provider: 
                    if not provider_from_user == provider:
                        logging.error("(BaseHandler.render_template) Logged in user does not match provider_key. We have a problem.")
                        
          
            if handler.auth.PATIENT_ROLE in roles:
                patient = data.db.get_patient_from_user(user)
                logging.info('(BaseHandler.render_template) Patient logged in: ' + user.get_email())
                if patient:
                    kw['patient'] = patient

        
        google_user = users.get_current_user()
        if google_user:
            logging.info('(BaseHandler.render_template) Google User also logged in: ' + str(google_user))
            kw['google_user'] = google_user

            # check google account for admin, add to roles
            if users.is_current_user_admin():
                roles.append(handler.auth.ADMIN_ROLE)
                
                # add fake login for current user
                kw['provider_from_user'] = kw['provider']

        
        # set the roles
        kw['roles'] = roles
            
        # set the language
        lang = self.get_language()
        logging.info('(BaseHandler.render_template) Language is %s' % lang)
        kw['lang'] = lang
        kw['other_languages'] = filter(lambda l: l not in lang, util.LANGUAGE_LABELS.keys())

        # Login and logout URLs (why is this coded here?)
        kw['login_url'] = '/login'
        kw['logout_url'] = '/logout'
        kw['admin_logout_url'] = users.create_logout_url('/')
        
        # useful constants for templates
        kw['category_dict'] = dict(util.get_all_categories())
        kw['specialty_dict'] = dict(util.getAllSpecialities())
        kw['certification_dict'] = dict(util.getAllCertifications())
        kw['association_dict'] = dict(util.getAllAssociations())

        kw['language_labels'] = util.LANGUAGE_LABELS
        
        
        # ---------------
        # Set this to true to show booking block on Index
        # ---------------
        
        site_config = db.get_site_config()
        if site_config:
            kw['site_config'] = site_config
            kw['booking_enabled'] = site_config.booking_enabled
            kw['google_analytics_enabled'] = site_config.google_analytics_enabled
            kw['facebook_like_enabled'] = site_config.facebook_like_enabled

        else:
            # no site configuration exists in database, create one
            site_config = SiteConfig()
            
            # take defaul state for booking enabled from util 
            # (so it can be set before the handler is called in unit tests)
            site_config.booking_enabled = util.BOOKING_ENABLED
            
            site_config.put()
            kw['site_config'] = site_config
            kw['booking_enabled'] = site_config.booking_enabled
            kw['google_analytics_enabled'] = site_config.google_analytics_enabled
            kw['facebook_like_enabled'] = site_config.facebook_like_enabled
        
        # render
                
        # check if we have internet exploder
        browser = self.request.headers.get('User-Agent')
        is_msie = re.match(".*MSIE.*", browser);
        logging.info("Browser: %s" % browser)

        if is_msie:            
            self.response.write(self.jinja2.render_template('internet_explorer.html', **kw))
            site_counter = db.get_site_counter()
            site_counter.internet_explorer_hits += 1
            site_counter.put_async()

        else:
            self.response.write(self.jinja2.render_template(filename, **kw))
        
        # log request in database
        log_entry = SiteLog()
        log_entry.language = self.get_language()
        log_entry.page = self.request.path
        log_entry.ip = self.request.remote_addr
        log_entry.referer= self.request.referer

        if user:
            log_entry.user_email = user.get_email()
            log_entry.user = user.key

        if google_user:
            log_entry.admin_email = google_user.email()

        log_entry.put_async()
          
    def dispatch(self):
        ''' 
            - Set language from session and 
            - Save the session across requests
        '''
        
        # language
        lang = self.get_language()
        if not lang:
            lang = util.DEFAULT_LANG
            
        self.install_translations(lang)

        # save session (from auth)
        try:
            super(BaseHandler, self).dispatch()
        finally:
            self.session_store.save_sessions(self.response)
            

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def auth_config(self):
        ''' Internal auth config '''
        auth_conf = { 'login_url': self.uri_for('login'),
                      'logout_url': self.uri_for('logout') }
        return auth_conf
    
    def get_language(self):
        session = self.session_store.get_session()
        if session.has_key('lang'):
            logging.info('(BaseHandler.get_language) get language from session = %s' % session['lang'])
            return session['lang']
        else:
            logging.info('(BaseHandler.get_language) no language in session, return default = %s' % util.DEFAULT_LANG)
            return util.DEFAULT_LANG
        
    def set_language(self, lang):
        logging.info('(BaseHandler.set_language) set session[lang] = %s' % lang)
        session = self.session_store.get_session()
        session['lang'] = lang
        
        
    def install_translations(self, lang):
        logging.info('(BaseHandler.install_translations) installing translations %s' % lang)

        # Set the requested locale.
        i18n.get_i18n().set_locale(lang)
        
        logging.info('(BaseHandler.install_translations) webapp2 i18n locale: %s' % i18n.get_i18n().locale)
    
    def login_user(self, email, password, remember_me=True):
        auth_user = self.auth.get_user_by_password(email, password, remember=remember_me)
        user = self.get_current_user()
        logging.info('(BaseHandler.login_user) Login succesful for %s' % user)
        return user

    def get_current_user(self):
        ''' Get the current authenticated user from our internal auth system. Returns None if no user is logged in'''
        user = None
        user_session = self.auth.get_user_by_session()
        logging.info('(BaseHandler.get_current_user) user_session:' + str(user_session))
        if user_session:
            user, token_timestamp = self.auth.store.user_model.get_by_auth_token(user_session['user_id'], user_session['token'])
        return user
    
    def create_empty_user_for_provider(self, provider):
        roles = [handler.auth.PROVIDER_ROLE]
        auth_id = provider.email
        user_created, new_user = self.auth.store.user_model.create_user(auth_id, roles=roles)
        
        if user_created:
            logging.info('(BaseHandler.create_empty_user_for_provider) Create shell user for provider: %s' % new_user.get_email())
            
            # link user to provider
            provider.user = new_user.key
            provider.put()
            
            # make sure user is saved properly
            new_user.put()
            
            return new_user
        else:
            logging.info('(BaseHandler.create_empty_user_for_provider) New shell user creation failed. Probably existing email: %s' % new_user.get_email())
            return None


    def create_empty_user_for_patient(self, patient):
        roles = [handler.auth.PATIENT_ROLE]
        auth_id = patient.email
        user_created, new_user = self.auth.store.user_model.create_user(auth_id, roles=roles)
        
        if user_created:
            logging.info('(BaseHandler.create_empty_user_for_patient) Create shell user for patient: %s' % new_user.get_email())
            
            # link user to provider
            patient.user = new_user.key
            patient.put()
            
            return new_user
        else:
            logging.info('(BaseHandler.create_empty_user_for_patient) New shell user creation failed. Probably existing email: %s' % new_user.get_email())
            return None


### Logging stuff
    def log_event(self, user = None, msg = None):
        event = LogEvent()
        
        # try to attach the event to a user
        if user:
            # this is probably not super efficient
            if isinstance(user, Key):
                event.user = user
            elif isinstance(user, User):
                event.user = user.key
        else:
            user = None
            
        referer = self.request.headers.get('Referer')
        if referer:
            event.referer = referer
        
        if msg:
            event.description = msg
            
        google_user = users.get_current_user()
        if google_user:
            # check google account for admin
            if users.is_current_user_admin():
                event.admin = True


        # save async so we don't slow anything down
        # don't really care if it doesn't work (not critical information)
        event.put_async()


### Token stuff
### with a dictionary for tokens { 'subject', token } this could be made generic

    def create_token(self, key):
        # create a token for the user
        salt = sha.new(str(random.random())).hexdigest()[:5]
        token = sha.new(salt + key).hexdigest()
        return token

    def create_signup_token(self, user):
        user.signup_token = self.create_token(user.get_email())
        user.confirmed = False
        
        user.put()
        
        return user.signup_token
    
    def validate_signup_token(self, token):
        user = db.get_user_from_signup_token(token)
        
        return user

    def delete_signup_token(self, user):
        user.signup_token = None
        
        # assume the user is confirmed 
        # (possibly faulty assumption - move this closer to where it's called)
        user.confirmed = True
        
        user.put()
        
        return user
    
    
    def create_resetpassword_token(self, user):
        user.resetpassword_token = self.create_token(user.get_email())        
        user.put()
        return user.resetpassword_token
    
    def validate_resetpassword_token(self, token):
        user = db.get_user_from_resetpassword_token(token)
        
        return user

    def delete_resetpassword_token(self, user):
        user.resetpassword_token = None        
        user.put()
        
        return user
    