import webapp2
import util
import logging
from base import BaseHandler
import admin
import db
from forms import BookingForm, PatientForm, ProviderProfileForm, ProviderAddressForm

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('index.html', form=BookingForm(self.request.GET))
        
    def post(self):
        form = BookingForm(self.request.POST)
        if form.validate():
            logging.info('booking post:' + str(self.request))
            db.storeBooking(self.request)
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
