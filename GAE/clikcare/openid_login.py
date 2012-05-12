from google.appengine.api import users
import webapp2
from webapp2_extras import jinja2


class LoginHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        j = jinja2.get_jinja2(app=self.app)

    def get(self):
        continue_url = self.request.GET.get('continue')
        openid_url = self.request.GET.get('openid')
        if not openid_url:
            self.response.write(self.jinja2.render_template('login.html', continue_url=continue_url))
        else:
            self.redirect(users.create_login_url(continue_url, None, openid_url))

# TODO
# Make a utility class for common environment setup with main


jinja_environment_args = {
        'autoescape': True,
        'extensions': [
            'jinja2.ext.autoescape',
            'jinja2.ext.with_',
            'jinja2.ext.i18n'   
        ]}


webapp2_config = {}
webapp2_config['webapp2_extras.jinja2'] = {
                                            'environment_args': jinja_environment_args
                                            } 

webapp2_config['webapp2_extras.i18n'] = {
                                         'translations_path': 'locale',
                                         'default_locale': 'fr'
                                         }


application = webapp2.WSGIApplication([ ('/_ah/login_required', LoginHandler)],
                                      debug=True,
                                      config=webapp2_config)
