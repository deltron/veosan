# -*- coding: utf-8 -*-

import os, logging
# GAE
import webapp2
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, DomainRoute

# veo
from util import dump
import util
from utilities import time
from handler import booking, provider, patient, provider_admin, admin, static, contact, language, user
from data.model import User
from google.appengine.ext import ndb


jinja_filters = {}
jinja_filters['format_datetime_with_weekday'] = time.format_datetime_with_weekday
jinja_filters['format_date_weekday_after'] = time.format_date_weekday_after
jinja_filters['format_datetime_full'] = time.format_datetime_full
jinja_filters['format_datetime_noseconds'] = time.format_datetime_noseconds
jinja_filters['format_datetime_withseconds_convert_east_tz'] = time.format_datetime_withseconds_convert_east_tz
jinja_filters['format_hour'] = time.format_hour
jinja_filters['format_30min_period'] = time.format_30min_period
jinja_filters['code_to_string'] = util.code_to_string
jinja_filters['dump'] = dump
jinja_filters['remove_empty_strings_from_list'] = util.remove_empty_strings_from_list
jinja_filters['markdown'] = util.markdown

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
                                         'default_locale': 'en',
                                         'default_timezone': 'America/Montreal',
                                         }

webapp2_config['webapp2_extras.sessions'] = {
                                             'secret_key': '82374y6ii899hy8-89308847-21u9x676',
                                             }

webapp2_config['webapp2_extras.auth'] = {
                                         'user_model': User,
                                         }


application = ndb.toplevel(webapp2.WSGIApplication([
                                       # handle custom domains
                                       # match everything that is not veosan.com
                                       DomainRoute(r'www.<domain:((?!veosan\.com).)*$>', [                                        
                                          Route('/', handler=static.DomainDispatcher)
                                       ]),
                                       
                                       # GAE Warmup Requests
                                       ('/_ah/warmup', static.WarmupHandler),
                                       
                                       # robots.txt and sitemap.xml for search engines
                                       ('/robots.txt', static.RobotsHandler),
                                       ('/sitemap.xml', static.SitemapHandler),
                                       
                                       # General pages
                                       ('/', booking.IndexHandler),
                                       
                                       
                                       # booking stuff
                                       ('/next', booking.SearchNextHandler),
                                       ('/full', booking.FullyBookedHandler),
                                       ('/contact', contact.ContactHandler),


                                       # Static Pages
                                       Route('/about', handler=static.StaticHandler, name='about'),
                                       Route('/careers', handler=static.StaticHandler, name='careers'),
                                       Route('/terms', handler=static.StaticHandler, name='terms'),
                                       Route('/privacy', handler=static.StaticHandler, name='privacy'),
                                       
                                       # Patient
                                       PathPrefixRoute('/patient', [
                                            Route('/bookings', patient.ListPatientBookings),
                                            Route('/new', patient.NewPatientHandler),
                                            Route('/book', booking.BookingHandler),
                                       ]),
                                  
                                       #signups
                                       PathPrefixRoute('/signup', [
                                            Route('/patient', user.PatientSignupHandler),
                                            Route('/provider', user.ProviderSignupHandler1),
                                            Route('/provider2', user.ProviderSignupHandler2),
                                            Route('/patient/<lang_key>', user.PatientSignupHandler),
                                            Route('/provider/<lang_key>', user.ProviderSignupHandler1),
                                       ]),
                                                    
                                       #provider
                                       PathPrefixRoute('/provider', [
                                            # display a status message to the provider (new, reset, etc)                                            PathPrefixRoute('/profile', [
                                            PathPrefixRoute('/message', [
                                                Route('/<msg_key>/<vanity_url>', provider.ProviderMessageHandler),
                                            ]),

                                            Route('/welcome/<vanity_url>', provider.WelcomeHandler),
                                            Route('/schedule/<vanity_url>', provider.ProviderScheduleHandler),
                                            Route('/bookings/<vanity_url>', provider.ProviderBookingsHandler),
                                                  
                                            # provider profile
                                            PathPrefixRoute('/profile', [
                                                Route('/<vanity_url>', provider.ProviderEditProfileHandler),
                                                Route('/photo/<vanity_url>', provider.ProviderProfilePhotoUploadHandler),
                                            ]),
                     
                                            # CV sections (Education, Work Experience)
                                            PathPrefixRoute('/cv', [
                                                Route('/<vanity_url>', provider.ProviderCVHandler),
                                                Route('/<section>/<vanity_url>/<operation>', provider.ProviderCVHandler),
                                                Route('/<section>/<vanity_url>/<operation>/<key>', provider.ProviderCVHandler),
                                            ]),
                                                                                                                                                                    
                                            # Address
                                            PathPrefixRoute('/address', [
                                                Route('/<vanity_url>', provider.ProviderEditAddressHandler),
                                            ]),

                                            # terms display
                                            Route('/terms/<vanity_url>', user.ProviderTermsHandler),
                                        ]),
                                       
                                       ('/login', user.LoginHandler),
                                       ('/logout', user.LogoutHandler),


                                       # user
                                       PathPrefixRoute('/user', [
                                            Route('/activation/<signup_token>', handler=user.ActivationHandler),
                                            Route('/password/<signup_token>', user.PasswordHandler),
                                            Route('/resetpassword', user.ResetPasswordHandler),
                                            Route('/resetpassword/<resetpassword_token>', handler=user.ResetPasswordHandler),
                                       ]),
                                       
                                       # sales material
                                       Route('/sales', static.SalesHandler),
                                       Route('/sales/<page>', static.SalesHandler),
                                       
                                       # admin
                                       Route('/admin', admin.AdminIndexHandler),

                                       PathPrefixRoute('/admin', [
                                           Route('/bookings', admin.AdminBookingsHandler),
                                           Route('/booking/<operation>/<bk>', admin.AdminBookingDetailHandler),
                                           Route('/providers', admin.AdminProvidersHandler),
                                           Route('/patients', admin.AdminPatientsHandler),
                                           Route('/data', admin.AdminDataHandler),
                                           Route('/data/stage', admin.AdminStageDataHandler),
                                           Route('/data/delete', admin.AdminDeleteDataHandler),

                                           Route('/site_config/<feature>', admin.AdminSiteConfigHandler),

                                           PathPrefixRoute('/provider', [
                                               # provider actions
                                               Route('/init', admin.NewProviderInitHandler),
                                               Route('/solicit/<vanity_url>', admin.NewProviderSolicitHandler),
                                               Route('/status', provider_admin.ProviderStatusHandler),
                                                                                                  
                                               # provider admin
                                               Route('/admin/<vanity_url>', provider_admin.ProviderAdministrationHandler),
                                            
                                               # custom domain
                                               Route('/domain/<vanity_url>', provider_admin.ProviderDomainHandler),
                                            
                                               # logs
                                               Route('/logs/<vanity_url>', provider_admin.ProviderEventLogHandler),

                                               Route('/notes/<vanity_url>', provider_admin.ProviderNotesHandler),
                                               Route('/notes/<vanity_url>/<operation>/<note_key>', provider_admin.ProviderNotesHandler),
                                               Route('/feature/<feature_switch>/<vanity_url>', provider_admin.ProviderFeaturesHandler),
                                            ]),
                                       ]),
                                       
                                       # language
                                       Route('/lang/<lang>', language.LanguageHandler),
                                       
                                       # if nothing above matches, try to find a provider
                                       # if this doesn't find someone it should throw a 404 (or back to index page?)
                                       Route('/<vanity_url>', handler=provider.ProviderPublicProfileHandler),
                                       Route('/<vanity_url>/', handler=provider.ProviderPublicProfileHandler),
                                      ], debug=True,
                                      config=webapp2_config))

