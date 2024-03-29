import logging, sha, random
from google.appengine.api import users
import webapp2
from webapp2_extras import auth, i18n, jinja2, sessions

# veo
import data
import handler.auth
import util
from data import db
from data.model import User, LogEvent
from google.appengine.ext.ndb.key import Key
import re
import mail
import urlparse
from data.model_pkg.site_model import SiteConfig, SiteLog
from utilities import language
import datetime

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
    
    
    def handle_exception(self, exception, debug_mode):
        logging.error(exception)
        
        site_config = db.get_site_config()
        
        kw = {}
        kw['site_config'] = site_config

        if site_config and site_config.error_email_enabled:
            mail.email_exception_report(self.request, exception)
            self.response.write(self.jinja2.render_template('error500.html', **kw))
        else:
            super(BaseHandler, self).handle_exception(exception, debug_mode)


    def render_template(self, filename, provider=None, **kw):
        '''
            Common template rendering function
        '''
                
        # domain setup
        domain_without_ports = self.request.host.split(":")[0]
        domain = domain_without_www = domain_without_ports.replace("www.", "")
        kw['domain_setup'] = db.get_domain_setup(domain_without_www)
        
        kw['valid_domains'] = util.DOMAINS
        
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
        logging.debug('(BaseHandler.render_template) Language is %s' % lang)
        kw['lang'] = lang
        kw['other_languages'] = filter(lambda l: l not in lang, util.LANGUAGE_LABELS.keys())

        # Login and logout URLs (why is this coded here? : Beacause historically for google users you had to call a method to get the login and logout urls)
        kw['login_url'] = '/' + lang + '/login'
        kw['logout_url'] = '/logout'
        kw['admin_logout_url'] = users.create_logout_url('/')
        
        kw['language_labels'] = util.LANGUAGE_LABELS
        kw['is_url_translatable'] = language.is_url_translatable(self.request.url)
        if kw['is_url_translatable']:
            kw['url_post_language'] = language.get_url_post_language(self.request.url)
        
        
        # make all session variables available to templates
        kw['session'] = self.session
        kw['host'] = self.request.host
        
        # ---------------
        # Site config
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
        kw['internet_explorer_old'] = False
        user_agent = self.request.headers.get('User-Agent')
        if user_agent:
            is_msie = re.search("MSIE ([0-9]{1,}[\.0-9]{0,})", user_agent);
            logging.debug("Browser User-Agent: %s" % user_agent)
    
            if is_msie:
                msie_str = is_msie.group()
                version_str = re.search("([0-9]{1,}[\.0-9]{0,})", msie_str)
    
                if version_str:
                    version = float(version_str.group())
                    if version < 9:
                        kw['internet_explorer_old'] = True
                        
                        #self.response.write(self.jinja2.render_template('internet_explorer.html', **kw))
                        site_counter = db.get_site_counter()
                        site_counter.internet_explorer_hits += 1
                        site_counter.put_async()
                else:
                    logging.error("Unable to parse version string for Internet Explorer: %s" % is_msie.group())
                    
        else:
            logging.error("Unable to parse empty user agent")
        
        self.response.write(self.jinja2.render_template(filename, **kw))
        
        self.log_entry()
        
        
        
    def log_entry(self):
        google_user = users.get_current_user()
        user = self.get_current_user()
        
        # log request in database
        log_entry = SiteLog()
        log_entry.language = self.get_language()
        log_entry.page = self.request.path
        log_entry.ip = self.request.remote_addr
        log_entry.referer = self.request.referer

        if "X-AppEngine-Country" in self.request.headers:
            log_entry.gae_country = self.request.headers["X-AppEngine-Country"]

        if "X-AppEngine-Region" in self.request.headers:
            log_entry.gae_region = self.request.headers["X-AppEngine-Region"]

        if "X-AppEngine-City" in self.request.headers:
            log_entry.gae_city = self.request.headers["X-AppEngine-City"]

        if "X-AppEngine-CityLatLong" in self.request.headers:
            log_entry.gae_city_lat_long = self.request.headers["X-AppEngine-CityLatLong"]

        if user:
            log_entry.user_email = user.get_email()
            log_entry.user = user.key

        if google_user:
            log_entry.admin_email = google_user.email()
            
        if self.session.has_key('prospect_id'):
            prospect_id = self.session['prospect_id']
            if prospect_id:
                prospect = db.get_prospect_from_prospect_id(prospect_id)
                
                if prospect_id:
                    log_entry.prospect_id = prospect_id
                
                if prospect:
                    log_entry.prospect = prospect.key
           
           
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
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    @webapp2.cached_property
    def auth_config(self):
        ''' Internal auth config '''
        auth_conf = { 'login_url': self.uri_for('login'),
                      'logout_url': self.uri_for('logout') }
        return auth_conf
    
    def get_language(self):
        # parse path and look for potential vanity url
        url = self.request.url
        url_obj = urlparse.urlparse(url)
        path = url_obj.path
        if path:
            path_no_slash = path.replace('/','')
        
        provider_from_vanity_url = db.get_provider_from_vanity_url(path_no_slash)

        # parse url and look for potential language
        url_language = language.get_language_from_url(self.request.url) 
        
        # look for a prospect
        prospect = None
        if self.session.has_key('prospect_id'):
            prospect_id = self.session['prospect_id']
            if prospect_id:
                prospect = db.get_prospect_from_prospect_id(prospect_id) 
        
        
        # set the best language based on information available to us in order of priority
        # 1. directly in URL
        # 2. from a logged in user
        # 3. from a provider's default language (if viewing their profile)
        # 4. from a prospect's preset language
        # 5. default system language
        if url_language:
            return url_language
        elif self.get_current_user():
            return self.get_current_user().language
        elif provider_from_vanity_url and provider_from_vanity_url.profile_language:
            return provider_from_vanity_url.profile_language
        elif prospect:
            return prospect.language
        else:
            return util.DEFAULT_LANG 
        
            
    def set_language(self, lang):
        logging.info('(BaseHandler.set_language) set session[lang] = %s' % lang)
        self.install_translations(lang)
        
    def set_language_from_url(self):
        lang = language.get_language_from_url(self.request.url)
        self.set_language(lang)
         
    def translate_url(self, url, lang):
        # check that url starts with /en or /fr
        orig_lang = language.get_language_from_url(url)
        if orig_lang:
            new_url = '/' + lang + url[3:]
            return new_url
        else:
            return url
        
    def install_translations(self, lang):
        logging.debug('(BaseHandler.install_translations) installing translations %s' % lang)
        # Set the requested locale.
        i18n.get_i18n().set_locale(lang)
        logging.debug('(BaseHandler.install_translations) webapp2 i18n locale: %s' % i18n.get_i18n().locale)
    
    def login_user(self, email, password, remember_me=True):
        auth_user = self.auth.get_user_by_password(email, password, remember=remember_me)
        user = self.get_current_user()
        user.last_login = datetime.datetime.now()
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
### 
    def create_token_oldstyle(self, key):
        # create a token for the user
        salt = sha.new(str(random.random())).hexdigest()[:5]
        token = sha.new(salt + key).hexdigest()
        return token

    
    def create_token(self, user, subject):
        token = User.token_model.create(user.key.id(), subject).token
        
        if subject == 'reset':
            user.resetpassword_token = token 
            user.put()
            return user

        return token
    
    def validate_token(self, token):
        token = User.token_model.query(User.token_model.token == token).get()
        
        user = None
        if token:
            user = User.get_by_id(int(token.user))
        
        return user
        
    def delete_token(self, token, subject=None):
        token = User.token_model.query(User.token_model.token == token).get()
        user = User.get_by_id(int(token.user))
        token.key.delete()
        
        if subject == 'reset':
            user.resetpassword_token = None        
            user.put()

        return None    
    
    def log_prospect(self, prospect_id = None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        
        if prospect:
            if "X-AppEngine-Country" in self.request.headers:
                prospect.gae_country = self.request.headers["X-AppEngine-Country"]
    
            if "X-AppEngine-Region" in self.request.headers:
                prospect.gae_region = self.request.headers["X-AppEngine-Region"]
    
            if "X-AppEngine-City" in self.request.headers:
                prospect.gae_city = self.request.headers["X-AppEngine-City"]
    
            if "X-AppEngine-CityLatLong" in self.request.headers:
                prospect.gae_city_lat_long = self.request.headers["X-AppEngine-CityLatLong"]
    
    
            self.set_language(prospect.language)
            
            prospect.landing_hits += 1
            prospect.put()
            self.session['prospect_id'] = prospect.prospect_id
            
            return prospect
            
            
    def set_gae_geography_from_headers(self, obj):
        # set location info from request
        if "X-AppEngine-Country" in self.request.headers:
            obj.gae_country = self.request.headers["X-AppEngine-Country"]
            
        if "X-AppEngine-Region" in self.request.headers:
            obj.gae_region = self.request.headers["X-AppEngine-Region"]

        if "X-AppEngine-City" in self.request.headers:
            obj.gae_city = self.request.headers["X-AppEngine-City"]
        
        if "X-AppEngine-CityLatLong" in self.request.headers:
            obj.gae_city_lat_long = self.request.headers["X-AppEngine-CityLatLong"]

    def get_domain(self):
        domain_without_ports = self.request.host.split(":")[0]
        domain_without_www = domain_without_ports.replace("www.", "")        
        return domain_without_www

    def get_domain_setup(self):
        domain_without_www = self.get_domain()
        domain_setup = data.db.get_domain_setup(domain_without_www)
        
        return domain_setup

        