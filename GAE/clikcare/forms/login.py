# -*- coding: utf-8 -*-

from wtforms import Form, PasswordField, TextField
from wtforms import validators
from custom_form import CustomBooleanField

class LoginForm(Form):
    email = TextField(_(u'Email').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    password = PasswordField(_(u'Password').decode("UTF-8"))
    remember_me = CustomBooleanField(_(u'Remember Me').decode("UTF-8"))
