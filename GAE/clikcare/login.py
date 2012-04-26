from google.appengine.api import users
from google.appengine.ext import webapp
import webapp2, logging

class LoginHandler(webapp.RequestHandler):
    def get(self):
        logging.info("LoginHandler Invoked")
        user = users.get_current_user()
        
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
            logging.info(greeting)
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/"))

        self.response.out.write("<html><body>%s</body></html>" % greeting)

webapp2_config = {}

webapp2_config['webapp2_extras.i18n'] = {
                                         'translations_path': 'locale',
                                         'default_locale': 'fr'
                                         }

login = webapp2.WSGIApplication([
                                       ('/_ah/login_required', LoginHandler)], debug=True,
                                      config=webapp2_config)
