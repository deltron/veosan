
import webapp2
from webapp2_extras import jinja2
from wtforms import Form, TextField, SelectField, SelectMultipleField, validators, widgets
import util
import logging
from base import BaseHandler
import admin


class BaseHandler(webapp2.RequestHandler):
        
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, **template_args):
        self.response.write(self.jinja2.render_template(filename, **template_args))

# WTF! WTF doesn't come with checkboxes out of the box
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

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


class ProviderAddressForm(Form):
    firstName = TextField('Pr&eacute;nom', [validators.Length(min=1, message='Pr&eacute;nom requis.')])
    lastName = TextField('Nom', [validators.Length(min=1, message='Nom requis.')])
    email = TextField('Courriel', [validators.Email(message='Addresse de courriel invalide.')])
    telephone = TextField('T&eacute;l&eacute;phone', [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message='Format 514-555-1212')])
    regions = SelectField('Lieu', choices=util.getAllRegions())
    address = TextField('Addresse', [validators.Length(min=10, message='Address requis.')])
    city = TextField('Ville', [validators.Length(min=10, message='Address requis.')])
    postalCode = TextField('Code Postal', [validators.Length(min=6, message='Address requis.')])

class ProviderProfileForm(Form):
    categories = SelectField('Cat&eacute;gorie', choices=util.getAllCategories())
    specialties = MultiCheckboxField('Sp&eacute;cialit&eacute;s', choices=util.getAllSpecialities())
    schools = SelectField('&Eacute;cole', choices=util.getAllSchools())
    degree = MultiCheckboxField('Diplome(s)', choices=util.getAllDiplomas())
    startYear = TextField('En pratique depuis', [validators.Length(min=4, max=4, message='Requis.')])


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
        form = ProviderProfileForm(self.request.POST)

        self.render_template('provider/profile.html', form=form)
    
    def post(self):
        form = ProviderProfileForm(self.request.POST)

        if form.validate():
            self.render_template('patient/profile.html', form=form) 
        else:
            self.render_template('patient/profile.html', form=form)

class ProviderAddressHandler(BaseHandler):
    def get(self):
        form = ProviderAddressForm(self.request.GET)
        self.render_template('provider/address.html', form=form)
        
    def post(self):
        form = ProviderAddressForm(self.request.POST)

        if form.validate():
            self.render_template('patient/book.html', form=form) 
        else:
            self.render_template('patient/address.html', form=form)

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
