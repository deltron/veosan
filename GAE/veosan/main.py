# -*- coding: utf-8 -*-

import os, logging
# GAE
import webapp2
# veo
from util import dump
import util
from utilities import time
from data.model import User
from google.appengine.ext import ndb
from routes.routes import create_routes



jinja_filters = {}
jinja_filters['string_to_datetime'] = time.string_to_datetime
jinja_filters['string_to_time'] = time.string_to_time
jinja_filters['format_weekday'] = time.format_weekday
jinja_filters['format_date_weekday_after'] = time.format_date_weekday_after
jinja_filters['format_datetime_full'] = time.format_datetime_full
jinja_filters['format_datetime_noseconds'] = time.format_datetime_noseconds
jinja_filters['format_datetime_booking_form'] = time.format_datetime_booking_form
jinja_filters['format_datetime_withseconds_convert_east_tz'] = time.format_datetime_withseconds_convert_east_tz
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


routes = create_routes()

application = ndb.toplevel(webapp2.WSGIApplication(routes, debug=True, config=webapp2_config))
