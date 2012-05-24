# -*- coding: utf-8 -*-

# GAE
import webapp2, logging
from webapp2 import Route
from webapp2_extras.routes import RedirectRoute
# clik
import util
from handler import booking, provider, auth, admin
from  handler.base import BaseHandler
from forms import ContactForm



class StaticHandler(BaseHandler):
    def get(self):
        template = "static/" + self.request.route.name + ".html"
        self.render_template(template)
        

class ContactHandler(BaseHandler):
    def get(self):
        self.render_template("contact.html", form=ContactForm(self.request.GET), sent=False)

    def post(self):
        contact_form = ContactForm(self.request.POST)
        if contact_form.validate():
            from_email = contact_form.email.data
            subject = contact_form.subject.data
            message = contact_form.message.data
            
            # send email
            # show confirmation page
            
            logging.info('Feedback from %s | subject: %s\n\nMESSAGE\n=========\n%s' % (from_email, subject, message))
            
            self.render_template('contact.html', form=contact_form, sent=True)
        else:
            self.render_template('contact.html', form=contact_form, sent=False)



            
            

 

jinja_filters = {}
jinja_filters['format_date_weekday_after'] = util.format_date_weekday_after
jinja_filters['format_datetime_full'] = util.format_datetime_full
jinja_filters['format_datetime_noseconds'] = util.formatDateTimeNoSeconds
jinja_filters['format_hour'] = util.format_hour
jinja_filters['format_30min_period'] = util.format_30min_period
jinja_filters['dump'] = util.dump

jinja_environment_args = {
        'autoescape': True,
        'extensions': [
            'jinja2.ext.autoescape',
            'jinja2.ext.with_',
            'jinja2.ext.i18n'   
        ]}


webapp2_config = {}
webapp2_config['webapp2_extras.jinja2'] = {
                                            'filters': jinja_filters,
                                            'environment_args': jinja_environment_args
                                            } 

webapp2_config['webapp2_extras.i18n'] = {
                                         'translations_path': 'locale',
                                         'default_locale': 'fr'
                                         }

webapp2_config['webapp2_extras.sessions'] = {
                                             'secret_key': '82374y6ii899hy8-89308847-21u9x676',
                                             }

application = webapp2.WSGIApplication([
                                       # General pages
                                       ('/', booking.IndexHandler),
                                       ('/full', booking.FullyBookedHandler),
                                       ('/contact', ContactHandler),
                                       
                                       # Static Pages
                                       Route('/about', handler=StaticHandler, name='about'),
                                       Route('/careers', handler=StaticHandler, name='careers'),
                                       Route('/terms', handler=StaticHandler, name='terms'),
                                       Route('/privacy', handler=StaticHandler, name='privacy'),
                                       
                                       # Patient
                                       ('/patient/booknew', booking.PatientBookForNewHandler),
                                       ('/patient/book', booking.PatientBookHandler),
                                       
                                       # provider
                                       ('/provider/login', provider.ProviderLoginHandler),
                                       ('/provider/profile', provider.ProviderEditProfileHandler),
                                       ('/provider/address', provider.ProviderEditAddressHandler),
                                       ('/provider/address/upload', provider.ProviderAddressUploadHandler),
                                       ('/provider/schedule', provider.ProviderScheduleHandler),
                                       ('/provider/terms', provider.ProviderTermsHandler),
                                       ('/provider/bookings', provider.ProviderBookingsHandler),
                                       ('/provider/administration', provider.ProviderAdministrationHandler),
                                       Route('/provider/activation/<activation_key>', handler=provider.ProviderActivationHandler),
                                       ('/serve/([^/]+)?', provider.ServeHandler), # temporary - to test file uploads
                                       # admin
                                       ('/admin/provider/init', admin.NewProviderInitHandler),
                                       ('/admin/provider/solicit', admin.NewProviderSolicitHandler),
                                       ('/admin', admin.AdminIndexHandler),
                                       ('/admin/bookings', admin.AdminBookingsHandler),
                                       ('/admin/providers', admin.AdminProvidersHandler),
                                       # auth
                                       ('/login', auth.LoginHandler),
                                       #('/create', auth_ CreateUserHandler),
                                        #RedirectRoute('/login/', auth_ LoginHandler, name='login', strict_slash=True),
                                        RedirectRoute('/logout/', auth.LogoutHandler, name='logout', strict_slash=True),
                                      ], debug=True,
                                      config=webapp2_config)

