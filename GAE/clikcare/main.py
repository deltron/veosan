# -*- coding: utf-8 -*-

import os, logging
# GAE
import webapp2
from webapp2 import Route
# clik
import util
from handler import booking, provider, provider_admin, auth, admin, static, contact, blob, language, user
from data.model import User

jinja_filters = {}
jinja_filters['format_date_weekday_after'] = util.format_date_weekday_after
jinja_filters['format_datetime_full'] = util.format_datetime_full
jinja_filters['format_datetime_noseconds'] = util.format_datetime_noseconds
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

template_path = os.path.dirname(__file__) + '/templates'
locale_path = os.path.dirname(__file__) + '/locale'

logging.info('setting template path to %s' % template_path)

webapp2_config['webapp2_extras.jinja2'] = {
                                            'template_path': template_path,
                                            'filters': jinja_filters,
                                            'environment_args': jinja_environment_args
                                            } 

webapp2_config['webapp2_extras.i18n'] = {
                                         'translations_path': locale_path,
                                         'default_locale': 'en'
                                         }

webapp2_config['webapp2_extras.sessions'] = {
                                             'secret_key': '82374y6ii899hy8-89308847-21u9x676',
                                             }

webapp2_config['webapp2_extras.auth'] = {
                                         'user_model': User,
                                         }


application = webapp2.WSGIApplication([
                                       # General pages
                                       ('/', booking.IndexHandler),
                                       ('/full', booking.FullyBookedHandler),
                                       ('/contact', contact.ContactHandler),
                                       
                                       # Static Pages
                                       Route('/about', handler=static.StaticHandler, name='about'),
                                       Route('/careers', handler=static.StaticHandler, name='careers'),
                                       Route('/terms', handler=static.StaticHandler, name='terms'),
                                       Route('/privacy', handler=static.StaticHandler, name='privacy'),
                                       
                                       # Patient
                                       ('/patient/booknew', booking.PatientBookForNewHandler),
                                       ('/patient/book', booking.PatientBookHandler),
                                  
                                       #provider
                                       ('/provider/schedule', provider.ProviderScheduleHandler),
                                       ('/provider/bookings', provider.ProviderBookingsHandler),
                                       
                                       # user
                                       ('/provider/terms', user.ProviderTermsHandler),
                                       ('/provider/password', user.ProviderPasswordHandler),
                                       ('/provider/resetpassword', user.ProviderResetPasswordHandler),
                                       Route('/provider/resetpassword/<resetpassword_key>', handler=user.ProviderResetPasswordHandler),
                                       Route('/provider/activation/<signup_token>', handler=user.ProviderActivationHandler),
                                       ('/provider/signup', user.ProviderSignupHandler),
                                       ('/login', user.LoginHandler),
                                       ('/logout', user.LogoutHandler),
                                       
                                       # admin
                                       ('/admin', admin.AdminIndexHandler),
                                       ('/admin/provider/init', admin.NewProviderInitHandler),
                                       ('/admin/provider/solicit', admin.NewProviderSolicitHandler),
                                       ('/admin/bookings', admin.AdminBookingsHandler),
                                       ('/admin/providers', admin.AdminProvidersHandler),                                       
                                            
                                       # provider admin
                                       ('/admin/provider', provider_admin.ProviderAdministrationHandler),
                                       ('/admin/provider/enable', provider_admin.ProviderEnableHandler),
                                       ('/admin/provider/profile', provider_admin.ProviderEditProfileHandler),
                                       ('/admin/provider/address', provider_admin.ProviderEditAddressHandler),
                                       ('/admin/provider/address/upload', provider_admin.ProviderAddressUploadHandler),
                                                                              
                             
                                       # blob
                                       ('/serve/([^/]+)?', blob.BlobServeHandler),
                                       
                                       # language
                                       Route('/lang/<lang>', language.LanguageHandler),
                                       
                                      ], debug=True,
                                      config=webapp2_config)

