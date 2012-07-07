# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField
from wtforms import validators
from custom_form import CustomBooleanField
import util
from webapp2_extras.i18n import lazy_gettext as _

class BookingForm(Form):
    category = SelectField(_(u'Category'))
    location = SelectField(_(u'Location'))
    homecare = CustomBooleanField(_(u'Receive care at home'))
    booking_date = SelectField(_(u'Date'))
    booking_time = SelectField(_(u'Time'))

class email_only_booking_form(Form):
    email = TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))])

