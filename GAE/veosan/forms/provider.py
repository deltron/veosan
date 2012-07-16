# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, FileField, TextAreaField, IntegerField, FloatField
from wtforms import validators
from custom_form import MultiCheckboxField, CustomBooleanField, CustomForm
import util
from webapp2_extras.i18n import lazy_gettext as _


# Profile

class ProviderProfileForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'category', SelectField(_(u'Category'), choices=util.get_all_categories()))
        setattr(form, 'specialty', MultiCheckboxField(_(u'Specialties'), choices=util.getAllSpecialities()))
        setattr(form, 'start_year', TextField(_(u'Active Since'), [validators.Length(min=4, max=4, message=_(u'Your first year of practice'))]))
        setattr(form, 'bio', TextAreaField(_(u'Biography')))
        setattr(form, 'quote', TextAreaField(_(u'Quote')))
        setattr(form, 'associations', MultiCheckboxField(_(u'Associations'), choices=util.getAllAssociations()))
        setattr(form, 'certifications', MultiCheckboxField(_(u'Certifications'), choices=util.getAllCertifications()))
        setattr(form, 'onsite', CustomBooleanField(_(u'I am willing to do on-site visits')))



# CV

class ProviderEducationForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'start_year', IntegerField(_(u'Start Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Your first year'))]))
        setattr(form, 'end_year' , IntegerField(_(u'End Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Your last year')), validators.Optional()]))
        setattr(form, 'school_name' , SelectField(_(u'School'), choices=util.get_all_schools()))   
        setattr(form, 'degree_type' , SelectField(_(u'Degree'), choices=util.get_all_degrees()))
        setattr(form, 'degree_title' , TextField(_(u'Degree Title')))
        setattr(form, 'description' , TextAreaField(_(u'Description')))

class ProviderExperienceForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'start_year', IntegerField(_(u'Start Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Your first year'))]))
        setattr(form, 'end_year', IntegerField(_(u'End Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Your last year')), validators.Optional()]))
        setattr(form, 'company_name', TextField(_(u'Company Name')))
        setattr(form, 'title', TextField(_(u'Position Title')))
        setattr(form, 'description', TextAreaField(_(u'Description')))

class ProviderContinuingEducationForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'year', IntegerField(_(u'Year'), [validators.NumberRange(min=1940, max=2100)]))
        setattr(form, 'month', IntegerField(_(u'Month'), [validators.NumberRange(min=1, max=12), validators.Optional()]))
        setattr(form, 'type', SelectField(_(u'Type'), choices=util.get_all_continuing_education_types()))    
        setattr(form, 'hours', FloatField(_(u'Hours'), [validators.NumberRange(min=0, max=1000), validators.Optional()]))
        setattr(form, 'title', TextField(_(u'Title')))
        setattr(form, 'description', TextAreaField(_(u'Description')))


# Photo

class ProviderPhotoForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'profile_photo', FileField(_(u'Upload')))


# Admin only

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

class ProviderNoteForm(Form):
    body = TextAreaField(_(u'Note'))
    note_type = SelectField(_(u'Type'), choices=util.get_all_note_types())
    
class ProviderStatusForm(Form):
    status = SelectField(_(u'Status'), choices=util.get_all_status_types())
