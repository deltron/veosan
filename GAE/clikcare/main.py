import os
import webapp2
from webapp2_extras import jinja2

class BaseHandler(webapp2.RequestHandler):
  @webapp2.cached_property
  def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

  def render_template(self, filename, **template_args):
        self.response.write(self.jinja2.render_template(filename, **template_args))

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('index.html', name=self.request.get('name'))
    
class PatientBookHandler(BaseHandler):
    def post(self):
        # get latest requests
        # prs = db.GqlQuery("SELECT * FROM PatientRequest ORDER BY createdOn DESC LIMIT 10")

        template_values = {
            'specialty': self.request.get("what"),
            'location': self.request.get("where"),
            'whenDate': self.request.get("whenDate"),
            'whenTime': self.request.get("whenTime"),
            'who': self.request.get("who")
        }
        self.render_template('patient/book.html', tv=template_values) 
    
class PatientNewHandler(BaseHandler):
    def get(self):
        self.render_template('patient/new.html', name=self.request.get('name'))

class ProviderProfileHandler(BaseHandler):
    def get(self):
        self.render_template('provider/profile.html', name=self.request.get('name'))

class ProviderScheduleHandler(BaseHandler):
    def get(self):
        self.render_template('provider/schedule.html', name=self.request.get('name'))

class ProviderTermsHandler(BaseHandler):
    def get(self):
        self.render_template('provider/terms.html', name=self.request.get('name'))

    
application = webapp2.WSGIApplication([
                                       ('/', IndexHandler),
                                       ('/patient/book', PatientBookHandler),
                                       ('/patient/new', PatientNewHandler),
                                       ('/provider/schedule', ProviderScheduleHandler),
                                       ('/provider/profile', ProviderProfileHandler),
                                       ('/provider/terms', ProviderTermsHandler)
                                       ], debug=True)
    
    
"""
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

"""
