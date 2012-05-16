import gettext
import webapp2
from webapp2_extras import jinja2
from google.appengine.api import users


# change to en and everything is english!
# todo: do we do /en/ /fr/ for every address or read it in the session somewhere?

lang = 'fr'
t = gettext.translation('clikcare', 'locale', languages=[lang], fallback='en')
t.install()

class BaseHandler(webapp2.RequestHandler):        
    @webapp2.cached_property
    def jinja2(self):
        j = jinja2.get_jinja2(app=self.app)
        j.environment.install_gettext_translations(t)
        return j

    def render_template(self, filename, **template_args):
        # add template arguments common to all templates
        user = users.get_current_user()
        template_args['user'] = user
        template_args['login_url'] = users.create_login_url()
        template_args['logout_url'] = users.create_logout_url("/")
        # roles
        roles = []
        if users.is_current_user_admin():
            roles.append('admin')
        template_args['roles'] = roles
        
        self.response.write(self.jinja2.render_template(filename, **template_args))