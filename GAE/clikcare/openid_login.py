import webapp2
from base import BaseHandler
from google.appengine.api import users
from main import webapp2_config


# Base URLs for OpenID provides, these will be jazzed up with user info later
providers = {
    'Google'   : 'gmail.com',
    'Yahoo'    : 'yahoo.com',
    'MySpace'  : 'myspace.com',
    'AOL'      : 'aol.com',
    'MyOpenID' : 'myopenid.com'
    # add more here
}

class LoginHandler(BaseHandler):
    def get(self):
        login_urls = {}
            
        for name, uri in providers.items():
            login_urls[name] = users.create_login_url(federated_identity=uri)
            
        self.response.write(self.jinja2.render_template('login.html', login_urls=login_urls))
      

application = webapp2.WSGIApplication([ ('/_ah/login_required', LoginHandler),
                                       ('/test_login', LoginHandler)
                                       ],
                                      debug=True,
                                      config=webapp2_config)
