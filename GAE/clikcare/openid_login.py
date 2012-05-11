from google.appengine.api import users
from google.appengine.ext import webapp
import webapp2, logging
from base import BaseHandler

class LoginHandler(BaseHandler):
    def get(self):
        
        continue_url = self.request.GET.get('continue')
        openid_url = self.request.GET.get('openid')
        if not openid_url:
            self.render_template('login.html', continue_url=continue_url)
        else:
            self.redirect(users.create_login_url(continue_url, None, openid_url))


webapp2_config = {}

webapp2_config['webapp2_extras.i18n'] = {
                                         'translations_path': 'locale',
                                         'default_locale': 'fr'
                                         }

openid_login = webapp2.WSGIApplication([
                                       ('/_ah/login_required', LoginHandler)], debug=True,
                                      config=webapp2_config)
