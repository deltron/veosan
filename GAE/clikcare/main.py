import os
import webapp2
from webapp2_extras import jinja2
from wtforms import Form, TextField, validators

class BaseHandler(webapp2.RequestHandler):
  @webapp2.cached_property
  def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

  def render_template(self, filename, **template_args):
        self.response.write(self.jinja2.render_template(filename, **template_args))

class BookingForm(Form):
    email = TextField('Courriel', [
                                   validators.Length(min=6, max=120, message='Little short for an email address?'),
                                   validators.Email(message='That\'s not a valid email address.')
                                ])
    

class IndexHandler(BaseHandler):
    def get(self):   
        form = BookingForm(self.request.GET)
        self.render_template('index.html', form=form)
        
    def post(self):
        form = BookingForm(self.request.POST)

        if form.validate():
            template_values = {
                               'what': self.request.get("what"),
                               'where': self.request.get("where"),
                               'date': self.request.get("date"),
                               'time': self.request.get("time"),
                               'email': form.email.data
            }
            self.render_template('patient/book.html', tv=template_values) 
        else:
            self.render_template('index.html', form=form)

    
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
                                       ('/patient/new', PatientNewHandler),
                                       ('/provider/schedule', ProviderScheduleHandler),
                                       ('/provider/profile', ProviderProfileHandler),
                                       ('/provider/terms', ProviderTermsHandler)
                                       ], debug=True)
