from wtforms import TextField, TextAreaField, SelectField
from wtforms import validators
from webapp2_extras.i18n import lazy_gettext as _
from wtforms import Form

# veo
from custom_form import CustomForm
from forms import custom_validators, custom_filters
import util

class ContactForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'from_email', TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))]))
        setattr(form, 'subject', TextField(_(u'Subject'), [validators.Length(min=3, message=_(u'Subject required.'))]))
        setattr(form, 'message_body', TextAreaField(_(u'Message')))

