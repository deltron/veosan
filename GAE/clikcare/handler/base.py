import logging, sha, random
import webapp2
from google.appengine.api import users
from webapp2_extras import jinja2
from webapp2_extras import auth
from webapp2_extras import sessions
import data
import handler.auth
from webapp2_extras import i18n
import util
from webapp2_extras.i18n import lazy_gettext as _
from data.model import User
from data import db

class BaseHandler(webapp2.RequestHandler):
    '''
        Base Handler for the whole site. Provides templating, user and authentication services
    '''
    
    _translations = None
    
    @webapp2.cached_property
    def jinja2(self):
        '''
            jinja2 renderer
        '''
        j = jinja2.get_jinja2(app=self.app)
        #if self._translations:
        #    logging.info('installing translations %s' % self.get_language())
        #    j.environment.install_gettext_translations(self._translations)
        #else:
        #    logging.info('no translations for jinja')
        return j

    def render_template(self, filename, provider=None, **template_args):
        '''
            Common template rendering function
        '''
        
        # add template arguments common to all templates
        user = self.get_current_user()

        
        # Eventually display the full name of the user (when linked to patient or provider profile)
        username = ''
        roles = []
        
        
        # somebody is logged in
        if user:
            logging.info('(BaseHandler.render_template) User logged in: %s with roles %s' % (user.get_email(), user.roles))

            username = user.auth_ids[0]
                        
            # extend roles
            roles.extend(user.roles)
            
            # is it a provider?
            if handler.auth.PROVIDER_ROLE in roles:
                provider_from_user = data.db.get_provider_from_user(user)
                logging.info('(BaseHandler.render_template) Provider logged in: ' + str(provider_from_user.email))

                # verify user->provider matches request->provider passed as paramater (ie. from request key)
                if provider: 
                    if not provider_from_user == provider:
                        logging.error("(BaseHandler.render_template) Logged in user does not match provider_key. We have a problem.") 
                else:
                    # if no provider from request key, set it from the user
                    # useful for making the drop-down menu keys when not requesting specific provider pages
                    provider = provider_from_user
                
        google_user = users.get_current_user()
        if google_user:
            logging.info('(BaseHandler.render_template) Google User also logged in: ' + str(google_user))
            
            # check google account for admin, add to roles
            if users.is_current_user_admin():
                roles.append(handler.auth.ADMIN_ROLE)

            
        # template variables
        lang = self.get_language()
        other_languages = filter(lambda l: l not in lang, util.LANGUAGE_LABELS.keys())

        template_args['user'] = user
        template_args['google_user'] = google_user
        template_args['username'] = username
        template_args['login_url'] = '/login'
        template_args['logout_url'] = '/logout'
        template_args['admin_logout_url'] = users.create_logout_url('/')
        template_args['roles'] = roles
        template_args['provider'] = provider
        template_args['lang'] = lang
        template_args['other_languages'] = other_languages
        template_args['language_labels'] = util.LANGUAGE_LABELS
        
        logging.info('(BaseHandler.render_template) Language is %s' % lang)

        # render
        self.response.write(self.jinja2.render_template(filename, **template_args))
          
    def dispatch(self):
        ''' 
            - Set language form session and 
            - Save the session across requests
        '''
        # language
        lang = self.get_language()
        if not lang:
            lang = util.DEFAULT_LANG
        self.install_translations(lang)
        # save session (from auth)
        try:
            response = super(BaseHandler, self).dispatch()
            #self.response.write(response)
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
            return session['lang']
        else:
            return util.DEFAULT_LANG
        
    def set_language(self, lang):
        session = self.session_store.get_session()
        session['lang'] = lang
        
        
    def install_translations(self, lang):
        logging.info('installing translations %s' % lang)
        # Set the requested locale.
        #locale = self.request.GET.get('locale', 'en')
        #logging.info('locale from request is %s' % locale)
        i18n.get_i18n().set_locale(lang)
        
        logging.info('i18n locale: %s' % i18n.get_i18n().locale)
        logging.info('i18n translations: %s' % i18n.get_i18n().translations)

        # install on Jinja too
        #self.jinja2.environment.install_gettext_translations(t)
        logging.info('language is %s' % _('en'))
        
    
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


    def create_signup_token(self, user):
        # create a token for the user
        salt = sha.new(str(random.random())).hexdigest()[:5]
        token = sha.new(salt + user.get_email()).hexdigest()
        
        user.signup_token = token
        user.confirmed = False
        
        user.put()
        
        return token
    
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
