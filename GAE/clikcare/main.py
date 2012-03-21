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
            'what': self.request.get("what"),
            'where': self.request.get("where"),
            'date': self.request.get("date"),
            'time': self.request.get("time"),
            'email': self.request.get("email")
        }
 
        self.render_template('patient/book.html', tv=template_values) 
    
class PatientNewHandler(BaseHandler):
    def post(self):
        template_values = {
            'what': self.request.get("what"),
            'where': self.request.get("where"),
            'date': self.request.get("date"),
            'time': self.request.get("time"),
            'email': self.request.get("email")
        }
          
        self.render_template('patient/new.html', tv=template_values)

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