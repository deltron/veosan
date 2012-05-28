# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField
from wtforms import validators

class NewProviderForm(Form):
    provider_email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])

