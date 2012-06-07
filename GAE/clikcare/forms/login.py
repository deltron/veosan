# -*- coding: utf-8 -*-

from wtforms import Form, PasswordField, TextField
from wtforms import validators
from custom_form import CustomBooleanField
from webapp2_extras.i18n import lazy_gettext


class LoginForm(Form):
    email = TextField(lazy_gettext(u'Email'), [validators.Email(message=lazy_gettext(u'Invalid email address.'))])
    password = PasswordField(lazy_gettext(u'Password'))
    remember_me = CustomBooleanField(lazy_gettext(u'Remember Me'))
