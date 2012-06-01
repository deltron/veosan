from wtforms import Form, TextField, TextAreaField
from wtforms import validators

class ContactForm(Form):
    from_email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    subject = TextField(_(u'Subject').decode("UTF-8"), [validators.Length(min=3, message='Subject required.')])
    message_body = TextAreaField(_(u'Message').decode("UTF-8"))
