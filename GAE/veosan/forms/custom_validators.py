from data import db
from wtforms import ValidationError
import webapp2
from webapp2 import BaseRoute
from webapp2_extras.routes import PathPrefixRoute
import re
import logging
import main

class UniqueVanityURL(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        vanity_url = field.data
    
        if vanity_url:
            # force the vanity URL to lowercase
            vanity_url = vanity_url.lower()

            # try to fetch a provider with this vanity URL
            provider = db.get_provider_from_vanity_url(vanity_url)
                        
            if provider:
                # taken
                raise ValidationError(self.message)
    
            else:
                #available
                pass


class ReservedVanityURL(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        vanity_url = field.data
    
        if vanity_url:
            # force the vanity URL to lowercase
            vanity_url = vanity_url.lower()
            
            # check if it conflicts with a route
            route_list = webapp2.get_app().router.match_routes
            regex_to_check = []
            for route in route_list:
                if isinstance(route, BaseRoute):
                    regex_to_check.append(route.template)
                elif isinstance(route, PathPrefixRoute):
                    regex_to_check.append(route.prefix)

            reserved_url = False
            for regex in regex_to_check:
                # remove leading slash
                regex = regex.replace("/", "", 1)
                # remove anything after trailing slash
                regex = regex.split("/")[0]
                
                if re.match(regex, vanity_url):
                    logging.info("Vanity URL %s matches REGEX %s" % (vanity_url, regex))
                    raise ValidationError(self.message)
            
            # does not contain a reserved word
            pass

class UniqueEmail(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        email = field.data
    
        if email:
            # try to fetch a provider with this email address
            provider = db.get_provider_from_email(email)
            
            if provider:
                # taken
                raise ValidationError(self.message)
    
            else:
                #available
                pass


class NoWhitespace(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if ' ' in field.data:
            raise ValidationError(self.message)
