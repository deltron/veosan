# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, FileField, PasswordField, TextAreaField
from wtforms import validators
from custom_form import MultiCheckboxField, CustomBooleanField
import util


    
class ProviderAddressForm(Form):
    prefix = TextField(_(u'Title').decode("UTF-8"))
    first_name = TextField(_(u'First Name').decode("UTF-8"), [validators.Length(min=1, message=_(u'First name is a required field').decode("UTF-8"))])
    last_name = TextField(_(u'Last Name').decode("UTF-8"), [validators.Length(min=1, message=_(u'Last name is a required field').decode("UTF-8"))])
    postfix = TextField(_(u'Credentials').decode("UTF-8"))
    phone = TextField(_(u'Telephone').decode("UTF-8"), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212').decode("UTF-8"))])
    location = SelectField(_(u'Location').decode("UTF-8"), choices=util.getAllRegions())
    address = TextField(_(u'Addresse').decode("UTF-8"), [validators.Length(min=5, message='Address requis.')])
    city = TextField(_(u'City').decode("UTF-8"), [validators.Length(min=3, message='Address requis.')])
    postal_code = TextField(_(u'Postal Code').decode("UTF-8"), [validators.Length(min=6, message='Address requis.')])
    
class ProviderPhotoForm(Form):
    profilePhoto = FileField(_(u'Upload').decode("UTF-8"))

class ProviderProfileForm(Form):
    category = SelectField(_(u'Category').decode("UTF-8"), choices=util.getAllCategories())
    specialty = MultiCheckboxField(_(u'Specialties').decode("UTF-8"), choices=util.getAllSpecialities())
    start_year = TextField(_(u'Active Since').decode("UTF-8"), [validators.Length(min=4, max=4, message='Your first year of practice')])
    bio = TextAreaField(_(u'Biography').decode("UTF-8"))
    quote = TextAreaField(_(u'Quote').decode("UTF-8"))
    associations = MultiCheckboxField(_(u'Associations').decode("UTF-8"), choices=util.getAllAssociations())
    certifications = MultiCheckboxField(_(u'Certifications').decode("UTF-8"), choices=util.getAllCertifications())
    onsite = CustomBooleanField(_(u'I am willing to do on-site visits').decode("UTF-8"))

    #key = TextField('key')
    
class ProviderTermsForm(Form):
    # terms agreement (required)
    terms_agreement = CustomBooleanField(_(u'I agree with the Terms of Service').decode("UTF-8"), [validators.Required(message=_(u'You must accept the terms to register').decode("UTF-8"))])
    # todo validate against exact first_name, last_name string
    #signature = TextField(_(u'Signature').decode("UTF-8"), [validators.Length(min=5, message='First name and last name as in address page')])

class ProviderPasswordForm(Form):
    #email = TextField(_(u'Email').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    password = PasswordField(_(u'Password').decode("UTF-8"), [validators.Length(min=6, message='Password needs at least 6 characters')])
    #remember_me = CustomBooleanField(_(u'Remember Me').decode("UTF-8"))
    
class ProviderLoginForm(Form):
    email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    password = PasswordField('Password')
