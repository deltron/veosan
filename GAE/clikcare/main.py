# -*- coding: utf-8 -*-

import os, logging
# GAE
import webapp2
from webapp2 import Route
# clik
from util import dump
import util
from utilities import time
from handler import booking, provider, patient, provider_admin, admin, static, contact, blob, language, user
from data.model import User


jinja_filters = {}
jinja_filters['format_datetime_with_weekday'] = time.format_datetime_with_weekday
jinja_filters['format_date_weekday_after'] = time.format_date_weekday_after
jinja_filters['format_datetime_full'] = time.format_datetime_full
jinja_filters['format_datetime_noseconds'] = time.format_datetime_noseconds
jinja_filters['format_hour'] = time.format_hour
jinja_filters['format_30min_period'] = time.format_30min_period
jinja_filters['code_to_string'] = util.code_to_string
jinja_filters['dump'] = dump

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
                                       ('/next', booking.SearchNextHandler),
                                       ('/full', booking.FullyBookedHandler),
                                       ('/contact', contact.ContactHandler),
                                       
                                       # Static Pages
                                       Route('/about', handler=static.StaticHandler, name='about'),
                                       Route('/careers', handler=static.StaticHandler, name='careers'),
                                       Route('/terms', handler=static.StaticHandler, name='terms'),
                                       Route('/privacy', handler=static.StaticHandler, name='privacy'),
                                       
                                       # Patient
                                       ('/patient/bookings', patient.ListPatientBookings),
                                       ('/patient/new', patient.NewPatientHandler),
                                       ('/patient/book', booking.BookingHandler),
                                  
                                       #provider
                                       ('/provider/schedule', provider.ProviderScheduleHandler),
                                       ('/provider/bookings', provider.ProviderBookingsHandler),
                                       
                                       # user
                                       ('/login', user.LoginHandler),
                                       ('/logout', user.LogoutHandler),
                                       ('/user/password', user.PasswordHandler),
                                       ('/user/resetpassword', user.ResetPasswordHandler),
                                       Route('/user/resetpassword/<resetpassword_token>', handler=user.ResetPasswordHandler),
                                       ('/provider/signup', user.ProviderSignupHandler),
                                       ('/provider/terms', user.ProviderTermsHandler),
                                       Route('/user/activation/<signup_token>', handler=user.ActivationHandler),

                                       # admin
                                       ('/admin', admin.AdminIndexHandler),
                                       ('/admin/provider/init', admin.NewProviderInitHandler),
                                       ('/admin/provider/solicit', admin.NewProviderSolicitHandler),
                                       ('/admin/bookings', admin.AdminBookingsHandler),
                                       ('/admin/providers', admin.AdminProvidersHandler),  
                                       ('/admin/patients', admin.AdminPatientsHandler),
                                       ('/admin/data', admin.AdminDataHandler),
                                       ('/admin/data/stage', admin.AdminStageDataHandler),
                                       ('/admin/data/delete', admin.AdminDeleteDataHandler),
                                       
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

