# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField
from wtforms import validators
from webapp2_extras.i18n import lazy_gettext

class NewProviderForm(Form):
    provider_email = TextField(lazy_gettext(u'E-mail Address'), [validators.Email(message=lazy_gettext(u'Invalid email address.'))])

