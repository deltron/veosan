# -*- coding: utf-8 -*-

from wtforms import Form, PasswordField, TextField
from wtforms import validators
from custom_form import CustomBooleanField
from webapp2_extras.i18n import lazy_gettext as _
import custom_filters

# veo
from custom_form import CustomForm
import custom_validators
from wtforms.fields.core import SelectField
import util
from wtforms.fields.simple import HiddenField


class DomainSetupForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'brand_name', TextField('Brand Name'))
        setattr(form, 'css_file', TextField('CSS File'))
