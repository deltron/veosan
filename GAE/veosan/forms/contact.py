from wtforms import TextField, TextAreaField, SelectField
from wtforms import validators
from webapp2_extras.i18n import lazy_gettext as _
from wtforms import Form

# veo
from custom_form import CustomForm

class ContactForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'from_email', TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))]))
        setattr(form, 'subject', TextField(_(u'Subject'), [validators.Length(min=3, message=_(u'Subject required.'))]))
        setattr(form, 'message_body', TextAreaField(_(u'Message')))

class SignupForm(Form):
    role = SelectField()
    from_email = TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Please enter your email address.'))])
    postal_code = TextField(_(u'Postal Code'), [validators.Length(min=6, message=_(u'Please enter your postal code.'))])
