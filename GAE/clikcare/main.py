# use django 1.2
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import cgi
import logging
from db import PatientRequest



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
        
        # get latest requests
        prs = db.GqlQuery("SELECT * FROM PatientRequest ORDER BY createdOn DESC LIMIT 10")

        template_values = {
            'what': cgi.escape(self.request.get("what")),
            'where': cgi.escape(self.request.get("where")),
            'when': cgi.escape(self.request.get("when")),
            'who': cgi.escape(self.request.get("who")),
            'prs': prs
            }
        path = os.path.join(os.path.dirname(__file__), 'fr/findhealth.html')
        self.response.out.write(template.render(path, template_values))
        
class NewPatient(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/new.html')
        self.response.out.write(template.render(path, template_values))

class Schedule(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/schedule.html')
        self.response.out.write(template.render(path, template_values))



application = webapp.WSGIApplication([('/', MainPage),
                                      ('/findhealth', FindHealth),
                                      ('/new', NewPatient),
                                      ('/schedule', Schedule)], 
                                     debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
