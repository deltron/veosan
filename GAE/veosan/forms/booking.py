# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField, HiddenField
from wtforms import validators
from custom_form import CustomBooleanField
import util
from webapp2_extras.i18n import lazy_gettext as _
from utilities import time
from custom_form import CustomForm
from forms import custom_validators


class AppointmentDetailsForLoggedInUser(CustomForm):
    def _set_fields(self, form):
        setattr(form, 'comments', TextAreaField(_(u'Comments for your appointment')))
        setattr(form, 'booking_date', HiddenField('booking_date'))
        setattr(form, 'booking_time', HiddenField('booking_time'))

class AppointmentDetailsForNewPatient(CustomForm):
    def _set_fields(self, form):
        setattr(form, 'email',TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))]))
        setattr(form, 'comments', TextAreaField(_(u'Comments for your appointment')))
        setattr(form, 'booking_date', HiddenField('booking_date'))
        setattr(form, 'booking_time', HiddenField('booking_time'))

class RegistrationDetailsForNewPatient(CustomForm):
    def _set_fields(self, form):
        setattr(form, 'first_name', TextField(_(u'First Name'), [validators.Length(min=1, message=_(u'First name is a required field'))]))
        setattr(form, 'last_name', TextField(_(u'Last Name'), [validators.Length(min=1, message=_(u'Last name is a required field'))]))
        setattr(form, 'telephone', TextField(_(u'Telephone'), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212'))]))
        setattr(form, 'password', PasswordField(_(u'Password'), [
                                validators.Length(min=6, message=_(u'Password must be at least 6 characters.')),
                                validators.EqualTo('password_confirm', _(u"Passwords do not match."))]))
        setattr(form, 'password_confirm', PasswordField(_(u'Password Confirmation')))

        setattr(form, 'booking_key', HiddenField('patient_key'))
        setattr(form, 'booking_date', HiddenField('booking_date'))
        setattr(form, 'booking_time', HiddenField('booking_time'))
        setattr(form, 'terms_agreement', CustomBooleanField(_(u'I agree with the Terms of Service'), [validators.Required(message=_(u'You must accept the terms to book an appointment'))]))
