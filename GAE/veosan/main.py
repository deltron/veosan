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
from handler.provider_pkg import network_handler, address_handler, cv_handler,\
    profile_handler, welcome_handler
from data.model import User
from google.appengine.ext import ndb
from handler.user_pkg import signup_handler


jinja_filters = {}
jinja_filters['format_weekday'] = time.format_weekday
jinja_filters['format_date_medium'] = time.format_date_medium
jinja_filters['format_datetime_with_weekday'] = time.format_datetime_with_weekday
jinja_filters['format_date_with_weekday'] = time.format_date_with_weekday
jinja_filters['format_date_weekday_after'] = time.format_date_weekday_after
jinja_filters['format_datetime_full'] = time.format_datetime_full
jinja_filters['format_datetime_noseconds'] = time.format_datetime_noseconds
jinja_filters['format_datetime_hour_min'] = time.format_datetime_hour_min
jinja_filters['format_datetime_booking_form'] = time.format_datetime_booking_form
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
                                       Route('/_ah/warmup', static.WarmupHandler),
                                       
                                       # robots.txt and sitemap.xml for search engines
                                       Route('/robots.txt', static.RobotsHandler),
                                       Route('/sitemap.xml', static.SitemapHandler),
                                       
                                       # General pages
                                       ('/', static.IndexHandler),
                                       Route('/en', static.IndexHandler, handler_method='get_en'),
                                       Route('/fr', static.IndexHandler, handler_method="get_fr"),
                                       Route('/hideside/<what>', static.HideSideHandler),
                                          
                                       # booking stuff
                                       Route('/next', booking.SearchNextHandler),
                                       Route('/full', booking.FullyBookedHandler),
                                       Route('/contact', contact.ContactHandler),
                                       Route('/search', booking.SearchIndexHandler),


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
                                            Route('/patient', signup_handler.PatientSignupHandler),
                                            Route('/provider', signup_handler.ProviderSignupHandler1),
                                            Route('/provider2', signup_handler.ProviderSignupHandler2),
                                            Route('/patient/<lang_key>', signup_handler.PatientSignupHandler),
                                            Route('/provider/<lang_key>', signup_handler.ProviderSignupHandler1),
                                       ]),
                                                    
                                       #provider
                                       PathPrefixRoute('/provider', [
                                            
                                            # display a status message to the provider (new, reset, etc)                                            PathPrefixRoute('/profile', [
                                            PathPrefixRoute('/message', [
                                                Route('/<msg_key>/<vanity_url>', welcome_handler.ProviderMessageHandler),
                                            ]),

                                            PathPrefixRoute('/welcome', [
                                                Route('/<vanity_url>', welcome_handler.WelcomeHandler),
                                                Route('/<vanity_url>/<disable>', welcome_handler.WelcomeHandler),
                                            ]),
                                                                     
                                            Route('/bookings/<vanity_url>', provider.ProviderBookingsHandler),
                                            
                                            PathPrefixRoute('/network', [
                                                Route('/<vanity_url>', network_handler.ProviderNetworkHandler),
                                                Route('/<vanity_url>/<operation>', network_handler.ProviderNetworkHandler),
                                                Route('/<vanity_url>/<operation>/<provider_key>', network_handler.ProviderNetworkHandler),
                                            ]),
                                                                     
                                            # provider profile
                                            PathPrefixRoute('/profile', [
                                                Route('/<vanity_url>', profile_handler.ProviderEditProfileHandler),
                                                Route('/photo/<vanity_url>', profile_handler.ProviderProfilePhotoUploadHandler),
                                            ]),
                     
                                            # CV sections (Education, Work Experience)
                                            PathPrefixRoute('/cv', [
                                                Route('/<vanity_url>', cv_handler.ProviderCVHandler),
                                                Route('/<section>/<vanity_url>/<operation>', cv_handler.ProviderCVHandler),
                                                Route('/<section>/<vanity_url>/<operation>/<key>', cv_handler.ProviderCVHandler),
                                            ]),
                                            
                                            # Schedule
                                            PathPrefixRoute('/schedule', [
                                                Route('/<vanity_url>', provider.ProviderScheduleHandler),
                                                Route('/<vanity_url>/<operation>', provider.ProviderScheduleHandler),
                                                Route('/<vanity_url>/<operation>/<day>/<start_time>', provider.ProviderScheduleHandler),
                                                Route('/<vanity_url>/<operation>/<key>', provider.ProviderScheduleHandler),
                                                
                                            ]),
                                                                                                                                                                                   
                                            # Address
                                            PathPrefixRoute('/address', [
                                                Route('/<vanity_url>', address_handler.ProviderEditAddressHandler),
                                                Route('/change_url/<vanity_url>', address_handler.ProviderChangeURLHandler),
                                            ]),

                                            # Search
                                            PathPrefixRoute('/search', [
                                                Route('/<vanity_url>', provider.ProviderSearchHandler),
                                            ]),

                                            # terms display
                                            #Route('/terms/<vanity_url>', user.ProviderTermsHandler),
                                            
                                            # upgrade account
                                            Route('/upgrade/<vanity_url>', welcome_handler.ProviderUpgradeHandler),

                                        ]),
                                       
                                       Route('/login', user.LoginHandler),
                                       Route('/login/<next_action>/<key>', user.LoginHandler),
                                       Route('/logout', user.LogoutHandler),
                                       
                                       # invitations
                                       Route('/invite/<invite_token>', user.InviteHandler),

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
                                           Route('/invites', admin.AdminInvitesHandler),
                                           Route('/dashboard', admin.AdminDashboardHandler),
                                           Route('/data', admin.AdminDataHandler),
                                           Route('/data/stage', admin.AdminStageDataHandler),
                                           Route('/data/delete', admin.AdminDeleteDataHandler),

                                           Route('/site_config/<feature>', admin.AdminSiteConfigHandler),

                                           PathPrefixRoute('/provider', [
                                               # provider actions
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
                                       Route('/lang/<lang>/<hide_side>', language.LanguageHandler),
                                       
                                       # if nothing above matches, try to find a provider
                                       # if this doesn't find someone it should throw a 404 (or back to index page?)
                                       
                                       # Public profile
                                       Route('/<vanity_url>', handler=provider.ProviderPublicProfileHandler),
                                       Route('/<vanity_url>/', handler=provider.ProviderPublicProfileHandler),
                                       
                                       # Display schedule
                                       Route('/<vanity_url>/book', booking.BookFromPublicProfileDisplaySchedule),
                                       Route('/<vanity_url>/book/date/<start_date>', booking.BookFromPublicProfileDisplaySchedule),
                                       
                                       # Actual booking & registration
                                       Route('/<vanity_url>/book/<book_date:\d{4}-\d{2}-\d{2}>/<book_time:\d{1,2}>', booking.BookFromPublicProfileRegistration),
                                       Route('/<vanity_url>/book/register', booking.BookFromPublicProfileRegistration),

                                       # Social network
                                       Route('/<vanity_url>/connect', network_handler.ProviderConnectHandler),
                                      ], debug=True,
                                      config=webapp2_config))

