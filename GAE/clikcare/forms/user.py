# -*- coding: utf-8 -*-

from wtforms import Form, PasswordField
from wtforms import validators
from custom_form import CustomBooleanField
from webapp2_extras.i18n import lazy_gettext as _

class ProviderTermsForm(Form):
    # terms agreement (required)
    terms_agreement = CustomBooleanField(_(u'I agree with the Terms of Service'), [validators.Required(message=_(u'You must accept the terms to register'))])
    
class ProviderPasswordForm(Form):
    password = PasswordField(_(u'Password'), [validators.Length(min=6, message=_(u'Password needs at least 6 characters')), validators.EqualTo('password_confirm', _(u"Passwords do not match"))])
    password_confirm = PasswordField(_(u'Password Confirmation'))
    
