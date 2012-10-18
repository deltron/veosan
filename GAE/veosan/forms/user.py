# -*- coding: utf-8 -*-

from wtforms import Form, PasswordField, TextField
from wtforms import validators
from custom_form import CustomBooleanField
from webapp2_extras.i18n import lazy_gettext as _
import custom_filters

# veo
from custom_form import CustomForm
import custom_validators
from wtforms.fields.core import SelectField
import util
from wtforms.fields.simple import HiddenField

class LoginForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'email', TextField(_(u'Email'),
                                validators=[validators.Email(message=_(u'Invalid email address.'))],
                                filters=[custom_filters.to_lowercase]           
                            ))
        setattr(form, 'password', PasswordField(_(u'Password')))
        setattr(form, 'remember_me', CustomBooleanField(_(u'Remember Me')))

class ProviderTermsForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'terms_agreement', CustomBooleanField(_(u'I agree with the Terms of Service'), [validators.Required(message=_(u'You must accept the terms to register'))]))
    
class PasswordForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'password', PasswordField(_(u'Password'), [
                                validators.Length(min=6, message=_(u'Password must be at least 6 characters.')),
                                validators.EqualTo('password_confirm', _(u"Passwords do not match."))]))
        setattr(form, 'password_confirm', PasswordField(_(u'Password Confirmation')))
    
    

class ProviderSignupForm1(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'first_name', TextField(_(u'First Name'), [validators.Length(min=2, message=_(u'First name required.'))]))
        setattr(form, 'last_name', TextField(_(u'Last Name'), [validators.Length(min=2, message=_(u'Last name required.'))]))
        setattr(form, 'email', TextField(_(u'E-mail Address'), validators=[
                                                      validators.Email(message=_(u'Invalid email address.')),
                                                      custom_validators.UniqueEmail(message=_(u'That address is already being used, please choose another one.')),
                                                     ],
                                                     filters=[custom_filters.to_lowercase]           
                                         ))

class ProviderSignupForm2(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'first_name', HiddenField(_(u'First Name'), [validators.Length(min=2, message=_(u'First name required.'))]))
        setattr(form, 'last_name', HiddenField(_(u'Last Name'), [validators.Length(min=2, message=_(u'Last name required.'))]))
        setattr(form, 'email', HiddenField(_(u'E-mail Address'), validators=[
                                                      validators.Email(message=_(u'Invalid email address.')),
                                                      custom_validators.UniqueEmail(message=_(u'That address is already being used, please choose another one.')),
                                                     ],
                                                     filters=[custom_filters.to_lowercase]           
                                         ))
        setattr(form, 'category', SelectField(_(u'Category'), choices=util.get_all_categories_for_profile_editing(self.domain),
                                              validators=[custom_validators.DisallowNoChoiceInSelect(message=_('Please choose an option from the list. If none of the options seems to fit, please choose "Other"'))]
                                              ))

        setattr(form, 'password', PasswordField(_(u'Password'), [
                                validators.Length(min=6, message=_(u'Password must be at least 6 characters.')),
                                validators.EqualTo('password_confirm', _(u"Passwords do not match."))]))
        setattr(form, 'password_confirm', PasswordField(_(u'Password Confirmation')))
        setattr(form, 'terms_agreement', CustomBooleanField(_(u'I agree with the Terms of Service'), default='True', validators=[validators.Required(message=_(u'You must accept the terms to continue.'))]))


class PatientSignupForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'first_name', TextField(_(u'First Name'), [validators.Length(min=2, message=_(u'First name required.'))]))
        setattr(form, 'last_name', TextField(_(u'Last Name'), [validators.Length(min=2, message=_(u'Last name required.'))]))
        setattr(form, 'email', TextField(_(u'E-mail Address'), validators=[
                                                      validators.Email(message=_(u'Invalid email address.')),
                                                      custom_validators.UniqueEmail(message=_(u'That address is already being used, please choose another one.')),
                                                     ],
                                                     filters=[custom_filters.to_lowercase]           
                                         ))


