# use django 1.2
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import cgi
import logging




class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/form.html')
        self.response.out.write(template.render(path, template_values))


class FindHealth(webapp.RequestHandler):
    def post(self):
        logging.info('findHealth:' + str(self.request))
        
        #guestbook_name=self.request.get('guestbook_name')
        #greetings_query = Greeting.all().ancestor(
        #    guestbook_key(guestbook_name)).order('-date')
        #greetings = greetings_query.fetch(10)

        #if users.get_current_user():
        #    url = users.create_logout_url(self.request.uri)
        #    url_linktext = 'Logout'
        #else:
        #    url = users.create_login_url(self.request.uri)
        #    url_linktext = 'Login'

        template_values = {
            'specialty': cgi.escape(self.request.get("selectSpecialty")),
            #'url': url,
            #'url_linktext': url_linktext,
        }
        path = os.path.join(os.path.dirname(__file__), 'fr/findhealth.html')
        self.response.out.write(template.render(path, template_values))
        


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/findhealth', FindHealth)], 
                                     debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
