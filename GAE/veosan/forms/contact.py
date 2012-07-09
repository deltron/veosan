from wtforms import TextField, TextAreaField, SelectField
from wtforms import validators
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras import i18n
from wtforms import Form

# veo
from custom_form import CustomForm


class ContactForm(CustomForm):
    def __init__(self):
        self.set_field('from_email', TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))]))
        self.set_field('subject', TextField(_(u'Subject'), [validators.Length(min=3, message=_(u'Subject required.'))]))
        self.set_field('message_body', TextAreaField(_(u'Message')))

class SignupForm(Form):
    role = SelectField()
    from_email = TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Please enter your email address.'))])
    postal_code = TextField(_(u'Postal Code'), [validators.Length(min=6, message=_(u'Please enter your postal code.'))])
