from wtforms import Form, TextField, TextAreaField
from wtforms import validators
from webapp2_extras.i18n import lazy_gettext as _

class ContactForm(Form):
    from_email = TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))])
    subject = TextField(_(u'Subject'), [validators.Length(min=3, message=_(u'Subject required.'))])
    message_body = TextAreaField(_(u'Message'))
