from data import db
from wtforms import ValidationError
import webapp2
from webapp2 import BaseRoute
from webapp2_extras.routes import PathPrefixRoute
import re
import logging
import main
from wtforms.validators import Required
import handler

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
            
            validated_url = handler.user_pkg.signup_handler.validate_vanity_url(vanity_url)
            
            # if the validated URL is different from the given url there was a problem
            # raise an exception
                            
            if validated_url != vanity_url:
                logging.info("Vanity URL matched a route")
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

class UniqueProspectID(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        prospect_id = field.data
    
        if prospect_id:
            # try to fetch a provider with this email address
            prospect = db.get_prospect_from_prospect_id(prospect_id)
            
            if prospect:
                # taken
                raise ValidationError(self.message)
    
            else:
                #available
                pass
                      
class UniqueCampaignName(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        proposed_campaign_name = field.data
        if proposed_campaign_name:
            # try to fetch a provider with this email address
            campaign = db.get_campaign_form_name(proposed_campaign_name)
            if campaign:
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

class DisallowNoChoiceInSelect(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if field.data == "nothing":
            raise ValidationError(self.message)


class RequiredIfOther(Required):
    # a validator which makes a field required if
    # another field is set to "other" (ie select field)

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIfOther, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if other_field.data == "other":
            super(RequiredIfOther, self).__call__(form, field)


class StartTimeAfterEndTime(object):
    # a validator which makes sure the end time is after
    # the start time

    def __init__(self, start_time_field, message=None, *args, **kwargs):
        self.start_time_field = start_time_field
        self.message = message

    def __call__(self, form, field):
        start_time_field = form._fields.get(self.start_time_field)
        if start_time_field is None:
            raise Exception('no field named "%s" in form' % self.start_time_field)
        if int(field.data) <= int(start_time_field.data):
            raise ValidationError(self.message)
