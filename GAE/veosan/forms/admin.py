# -*- coding: utf-8 -*-

from wtforms import Form, PasswordField, TextField
from wtforms import validators
from custom_form import CustomBooleanField
from webapp2_extras.i18n import lazy_gettext as _
import custom_filters

# veo
from custom_form import CustomForm
import custom_validators
from wtforms.fields.core import SelectField, BooleanField
import util
from wtforms.fields.simple import HiddenField, TextAreaField


class DomainSetupForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'brand_name', TextField('Brand Name (lowercase)'))
        setattr(form, 'brand_name_case', TextField('Brand Name (proper case)'))
        setattr(form, 'css_file', TextField('CSS File'))
        setattr(form, 'categories_json', TextAreaField('Categories (JSON string)',  
                                                       validators=[custom_validators.JSONValidator()]))
        setattr(form, 'specialties_display', BooleanField('Display Specialties'))
        setattr(form, 'specialties_json', TextAreaField('Specialties (JSON string)',  
                                                       validators=[custom_validators.JSONValidator()]))
        setattr(form, 'associations_json', TextAreaField('Associations (JSON string)',  
                                                       validators=[custom_validators.JSONValidator()]))

