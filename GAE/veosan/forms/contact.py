from wtforms import TextField, TextAreaField, SelectField
from wtforms import validators
from webapp2_extras.i18n import lazy_gettext as _
from wtforms import Form

# veo
from custom_form import CustomForm
from forms import custom_validators

class ContactForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'from_email', TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))]))
        setattr(form, 'subject', TextField(_(u'Subject'), [validators.Length(min=3, message=_(u'Subject required.'))]))
        setattr(form, 'message_body', TextAreaField(_(u'Message')))

class NewProviderForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'vanity_url', TextField(_(u'Account name'), [
                                              validators.Length(min=6, message=_('Your personal address requires at least 6 characters.')), 
                                              custom_validators.UniqueVanityURL(message=_(u'That address is already being used, please choose another one.')),
                                              custom_validators.ReservedVanityURL(message=_(u'That address is already being used, please choose another one.')),
                                              validators.Regexp(u'^[a-zA-Z0-9]+$', message=_(u'Your personal address can only contain letters and numbers.')),
                                              ]))
    
        setattr(form, 'email', TextField(_(u'E-mail Address'), [
                                                      validators.Email(message=_(u'Invalid email address.')),
                                                      custom_validators.UniqueEmail(message=_(u'That address is already being used, please choose another one.')),
                                                     ]))



# old
class TeaserForm(Form):
    role = SelectField()
    from_email = TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Please enter your email address.'))])
    postal_code = TextField(_(u'Postal Code'), [validators.Length(min=6, message=_(u'Please enter your postal code.'))])
