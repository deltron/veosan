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
from db import Booking



class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/form.html')
        self.response.out.write(template.render(path, template_values))


class FindHealth(webapp.RequestHandler):
    def post(self):
        #logging.info('findHealth:' + str(self.request))
        booking = Booking()
        booking.requestSpecialty = cgi.escape(self.request.get("what"))
        booking.requestLocation = cgi.escape(self.request.get("where"))
        booking.requestDate = cgi.escape(self.request.get("whenDate"))
        booking.requestTime = cgi.escape(self.request.get("whenTime"))
        booking.requestContact = cgi.escape(self.request.get("who"))
        booking.put()
        
        # get latest requests
        prs = db.GqlQuery("SELECT * FROM Booking ORDER BY createdOn DESC LIMIT 10")

        template_values = {
            'specialty': booking.requestSpecialty,
            'location': booking.requestLocation,
            'whenDate': booking.requestDate,
            'whenTime': booking.requestTime,
            'who': booking.requestContact,
            'prs': prs
            }
        path = os.path.join(os.path.dirname(__file__), 'fr/findhealth.html')
        self.response.out.write(template.render(path, template_values))
        
class NewPatient(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/new.html')
        self.response.out.write(template.render(path, template_values))

class ProviderProfile(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/provider/profile.html')
        self.response.out.write(template.render(path, template_values))


class ProviderSchedule(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/provider/schedule.html')
        self.response.out.write(template.render(path, template_values))

class ProviderTerms(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'fr/provider/terms.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/findhealth', FindHealth),
                                      ('/patient', NewPatient),
                                      
                                      ('/provider/terms', ProviderTerms),
                                      ('/provider/schedule', ProviderSchedule), 
                                      ('/provider/profile', ProviderProfile)], 
                                     debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
