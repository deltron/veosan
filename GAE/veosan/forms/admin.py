from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField
from wtforms import validators
from webapp2_extras.i18n import lazy_gettext as _

# veo
import custom_validators

class NewProviderForm(Form):
    vanity_url = TextField(_(u'Vanity URL'), [
                                              validators.Length(min=4, message='Vanity URL should be at least 4 characters'), 
                                              custom_validators.UniqueVanityURL(message=_(u'That name is already taken, please choose another one.')),
                                              custom_validators.ReservedVanityURL(message=_(u'That URL contains a reserved word.')),
                                              custom_validators.NoWhitespace(message=_(u'Vanity URL cannot contain whitespace')),
                                              ])
    
    provider_email = TextField(_(u'E-mail Address'), [
                                                      validators.Email(message=_(u'Invalid email address.')),
                                                      custom_validators.UniqueEmail(message=_(u'Provider already exists for email address.')),
                                                     ])

