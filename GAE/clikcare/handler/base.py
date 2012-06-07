import gettext, os, logging
import webapp2
from google.appengine.api import users
from webapp2_extras import jinja2
from webapp2_extras import auth
from webapp2_extras import sessions
import data


# change to en and everything is english!
# todo: do we do /en/ /fr/ for every address or read it in the session somewhere? Session.

lang = 'fr'
locale_dir = os.path.dirname(__file__) + '/../locale'
t = gettext.translation('clikcare', locale_dir, languages=[lang], fallback='en')
t.install()

class BaseHandler(webapp2.RequestHandler):
    '''
        Base Handler for the whole site. Provides templating, user and authentication services
    '''
    
    @webapp2.cached_property
    def jinja2(self):
        '''
            jinja2 renderer
        '''
        j = jinja2.get_jinja2(app=self.app)
        j.environment.install_gettext_translations(t)
        return j

    def render_template(self, filename, **template_args):
        '''
            Common template rendering function
        '''
        # add template arguments common to all templates
        user = self.get_current_user()
        logging.info('User: ' + str(user))
        # Eventually display the full name of the user (when linked to patient or provider profile)
        username = ''
        roles = []

        if user:
            username = user.auth_ids[0]
            
            # extend roles
            roles.extend(user.roles)
            
            # make provider object available if a provider
            provider = data.db.get_provider_from_email(user.get_email())

            
        google_user = users.get_current_user()
        if google_user:
            logging.info('google user also logged in:' + str(google_user))
            #username = '%s [%s]' % (username, google_user.nickname())
            
            # check google account for admin, add to roles
            if users.is_current_user_admin():
                roles.append('admin')
        else:
            logging.info('no google user logged in')
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
        # render
        self.response.write(self.jinja2.render_template(filename, **template_args))
          
    def dispatch(self):
        '''Save the session across requests'''
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
    
    
    def login_user(self, email, password, remember_me=True):
        auth_user = self.auth.get_user_by_password(email, password, remember=remember_me)
        user = self.get_current_user()
        logging.info('Login succesful for %s' % user)
        return user

    def get_current_user(self):
        ''' Get the current authenticated user from our internal auth system. Returns None if no user is logged in'''
        user = None
        user_session = self.auth.get_user_by_session()
        logging.info('user_session:' + str(user_session))
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

               
                     
                     
                     