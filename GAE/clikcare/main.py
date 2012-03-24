
import webapp2
from wtforms import Form, TextField, SelectField, validators
import util
import logging
from base import BaseHandler
import admin


class BookingForm(Form):
    email = TextField('Courriel', [validators.Email(message='Addresse de courriel invalide.')])
    categories = SelectField('Cat&eacute;gorie', choices=util.getAllCategories())
    regions = SelectField('Lieu', choices=util.getAllRegions())
    dates = SelectField('Date', choices=util.getDatesList())
    times = SelectField('Heure', choices=util.getTimesList())


class PatientForm(Form):
    firstName = TextField('Pr&eacute;nom', [validators.Length(min=1, message='Pr&eacute;nom requis.')])
    lastName = TextField('Nom', [validators.Length(min=1, message='Nom requis.')])
    email = TextField('Courriel', [validators.Email(message='Addresse de courriel invalide.')])
    telephone = TextField('T&eacute;l&eacute;phone', [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message='Format 514-555-1212')])


class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('index.html', form=BookingForm(self.request.GET))
        
    def post(self):
        form = BookingForm(self.request.POST)
        # validation
        if form.validate():
            logging.info('booking post:' + str(self.request))

            db.storeBooking(request)

            
            self.render_template('patient/new.html', form=PatientForm(self.request.POST)) 
        else:
            self.render_template('index.html', form=form)

    
class PatientBookHandler(BaseHandler):
    def post(self):
        form = PatientForm(self.request.POST)

        if form.validate():
            # Store Booking
            self.render_template('patient/book.html', form=form) 
        else:
            self.render_template('patient/new.html', form=form)

class ProviderProfileHandler(BaseHandler):
    def get(self):
        self.render_template('provider/profile.html', name=self.request.get('name'))

class ProviderAddressHandler(BaseHandler):
    def get(self):
        self.render_template('provider/address.html', name=self.request.get('name'))

class ProviderScheduleHandler(BaseHandler):
    def get(self):
        self.render_template('provider/schedule.html', name=self.request.get('name'))

class ProviderTermsHandler(BaseHandler):
    def get(self):
        self.render_template('provider/terms.html', name=self.request.get('name'))




jinja_filters = {}
jinja_filters['formatdate'] = util.formatDateFR

webapp2_config = {}
webapp2_config['webapp2_extras.jinja2'] = {
                                            'filters': jinja_filters
                                            } 

application = webapp2.WSGIApplication([
                                       ('/', IndexHandler),
                                       ('/patient/book', PatientBookHandler),
                                       ('/provider/schedule', ProviderScheduleHandler),
                                       ('/provider/address', ProviderAddressHandler),
                                       ('/provider/profile', ProviderProfileHandler),
                                       ('/provider/terms', ProviderTermsHandler),
                                       ('/admin', admin.IndexHandler)
                                       ], debug=True,
                                      config=webapp2_config)
