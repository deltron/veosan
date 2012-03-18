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
import db.PatientRequest



class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/form.html')
        self.response.out.write(template.render(path, template_values))


class FindHealth(webapp.RequestHandler):
    def post(self):
        #logging.info('findHealth:' + str(self.request))
        pr = PatientRequest()
        pr.specialty = cgi.escape(self.request.get("what"))
        pr.location = cgi.escape(self.request.get("where"))
        pr.when = cgi.escape(self.request.get("when"))
        pr.who = cgi.escape(self.request.get("who"))
        pr.put()

        template_values = {
            'what': cgi.escape(self.request.get("what")),
            'where': cgi.escape(self.request.get("where")),
            'when': cgi.escape(self.request.get("when")),
            'who': cgi.escape(self.request.get("who"))
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
