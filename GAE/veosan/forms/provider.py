# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, FileField, TextAreaField
from wtforms import validators
from custom_form import MultiCheckboxField, CustomBooleanField
import custom_validators
import util
from webapp2_extras.i18n import lazy_gettext as _



class ProviderAddressForm(Form):
    title = TextField(_(u'Title'))
    first_name = TextField(_(u'First Name'), [validators.Length(min=1, message=_(u'First name is a required field'))])
    last_name = TextField(_(u'Last Name'), [validators.Length(min=1, message=_(u'Last name is a required field'))])
    credentials = TextField(_(u'Credentials'))
    phone = TextField(_(u'Telephone'), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212'))])
    location = SelectField(_(u'Location'), choices=util.get_all_regions())
    address = TextField(_(u'Addresse'), [validators.Length(min=5, message='Address requis.')])
    city = TextField(_(u'City'), [validators.Length(min=3, message='Address requis.')])
    postal_code = TextField(_(u'Postal Code'), [validators.Length(min=6, message='Address requis.')])
    vanity_url = TextField(_(u'Vanity URL'), [
                                              validators.Length(min=4, message='Vanity URL should be at least 4 characters'), 
                                              custom_validators.UniqueVanityURL(message=_(u'That name is already taken, please choose another one.'))
                                              ])




class ProviderPhotoForm(Form):
    profilePhoto = FileField(_(u'Upload'))

class ProviderProfileForm(Form):
    category = SelectField(_(u'Category'), choices=util.get_all_categories())
    specialty = MultiCheckboxField(_(u'Specialties'), choices=util.getAllSpecialities())
    start_year = TextField(_(u'Active Since'), [validators.Length(min=4, max=4, message='Your first year of practice')])
    bio = TextAreaField(_(u'Biography'))
    quote = TextAreaField(_(u'Quote'))
    associations = MultiCheckboxField(_(u'Associations'), choices=util.getAllAssociations())
    certifications = MultiCheckboxField(_(u'Certifications'), choices=util.getAllCertifications())
    onsite = CustomBooleanField(_(u'I am willing to do on-site visits'))
