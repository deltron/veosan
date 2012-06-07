import os, logging
import webapp2
from google.appengine.api import users
from webapp2_extras import jinja2
from webapp2_extras import auth
from webapp2_extras import sessions
import data
from webapp2_extras import i18n
from util import languages
from webapp2_extras.i18n import lazy_gettext as _

# change to en and everything is english!
# todo: do we do /en/ /fr/ for every address or read it in the session somewhere? Session.

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
        logging.info('(BaseHandler.render_template) User logged in: ' + str(user))
        
        # Eventually display the full name of the user (when linked to patient or provider profile)
        username = ''
        roles = []
        
        
        # somebody is logged in
        if user:
            username = user.auth_ids[0]
                        
            # extend roles
            roles.extend(user.roles)
            
            # is it a provider?
            if 'provider' in roles:
                provider_from_user = data.db.get_provider_from_email(user.get_email())
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
                roles.append('admin')

        else:
            logging.info('(BaseHandler.render_template) No Google user logged in')
            # copy roles into roles list
            
        # template variables
        template_args['user'] = user
        template_args['google_user'] = google_user
        template_args['username'] = username
        template_args['login_url'] = '/login'
        template_args['logout_url'] = '/logout'
        template_args['admin_logout_url'] = users.create_logout_url('/')
        template_args['roles'] = roles
        template_args['provider'] = provider
		template_args['lang'] = _('en')
        template_args['languages'] = filter(lambda l: l not in [_('en')], languages)
        logging.info('language is %s' % _('en'))
            
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
            lang = 'fr'
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
            return 'fr'
        
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
        #t = gettext.translation('clikcare', locale_dir, languages=[lang], fallback='en')
        #t.install()
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
    
    def create_user(self, email, password, roles=[]):
        # Passing password_raw=password will hash the password
        
        user_created, new_user = self.auth.store.user_model.create_user(email, password_raw=password, roles=roles)
        if user_created:
            logging.info('Create new user: %s' % new_user)
            return new_user
        else:
            logging.info('New user creation failed. Probably existing email: %s' % new_user)
            return None

