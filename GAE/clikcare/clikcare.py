# use django 1.2
import os

import jinja2
import os
import webapp2

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# This causes error 500 in GAE
#from db import PatientRequest



class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('fr/form.html')
        self.response.out.write(template.render(template_values))


class FindHealth(webapp2.RequestHandler):
    def post(self):
        #logging.info('findHealth:' + str(self.request))
        pr = PatientRequest()
        pr.specialty = cgi.escape(self.request.get("what"))
        pr.location = cgi.escape(self.request.get("where"))
        pr.whenDate = cgi.escape(self.request.get("whenDate"))
        pr.whenTime = cgi.escape(self.request.get("whenTime"))
        pr.who = cgi.escape(self.request.get("who"))
        pr.put()
        
        # get latest requests
        prs = db.GqlQuery("SELECT * FROM PatientRequest ORDER BY createdOn DESC LIMIT 10")

        template_values = {
            'specialty': pr.specialty,
            'location': pr.location,
            'whenDate': pr.whenDate,
            'whenTime': pr.whenTime,
            'who': pr.who,
            'prs': prs
            }
        template = jinja_environment.get_template('fr/findhealth.html')
        self.response.out.write(template.render(template_values))

        
class NewPatient(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('fr/new.html')
        self.response.out.write(template.render(template_values))

class ProviderProfile(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('fr/provider/profile.html')
        self.response.out.write(template.render(template_values))


class ProviderSchedule(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('fr/provider/schedule.html')
        self.response.out.write(template.render(template_values))

class ProviderTerms(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('fr/provider/terms.html')
        self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/', MainPage),
                                      ('/findhealth', FindHealth),
                                      ('/patient', NewPatient),
                                      ('/provider/terms', ProviderTerms),
                                      ('/provider/schedule', ProviderSchedule),
                                      ('/provider/profile', ProviderProfile)],
                                     debug=True)
