# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField
from wtforms import validators
from custom_form import CustomBooleanField, CustomForm
import util
from webapp2_extras.i18n import lazy_gettext as _
from wtforms.fields.simple import HiddenField
from forms import custom_filters

class PatientForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'first_name', TextField(_(u'First Name'), [validators.Length(min=1, message=_(u'First name is a required field'))]))
        setattr(form, 'last_name', TextField(_(u'Last Name'), [validators.Length(min=1, message=_(u'Last name is a required field'))]))
        setattr(form, 'telephone', HiddenField(_(u'Telephone'), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212'))]))
        setattr(form, 'email', HiddenField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))]))
        setattr(form, 'terms_agreement', CustomBooleanField(_(u'I agree with the Terms of Service'), [validators.Required(message=_(u'You must accept the terms to book an appointment'))]))

