import gettext
import webapp2
import logging
from google.appengine.api import users
from webapp2_extras import jinja2
from webapp2_extras import auth
from webapp2_extras import sessions


# change to en and everything is english!
# todo: do we do /en/ /fr/ for every address or read it in the session somewhere?

lang = 'fr'
t = gettext.translation('clikcare', 'locale', languages=[lang], fallback='en')
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
        user = self.get_current_auth_user()
        logging.info('User:' + str(user))
        # Eventually display the full name of the user (when linked to patient or provider profile)
        username = ''
        if user:
            username = user.auth_ids[0]
        # roles
        roles = []
        google_user = users.get_current_user()
        if google_user:
            logging.info('google user also logged in:' + str(google_user))
            username = '%s [%s]' % (username, google_user.nickname())
            # check google account for admin
            if users.is_current_user_admin():
                roles.append('admin')
        else:
            logging.info('no google user logged in')
        # template variables
        template_args['username'] = username
        template_args['login_url'] = '/login'
        template_args['logout_url'] = '/logout'
        template_args['roles'] = roles
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

    def get_current_auth_user(self):
        ''' Get the current authenticated user from our internal auth system'''
        user = None
        user_session = self.auth.get_user_by_session()
        logging.info('user_session:' + str(user_session))
        if user_session:
            user, token_timestamp = self.auth.store.user_model.get_by_auth_token(user_session['user_id'], user_session['token'])
        return user