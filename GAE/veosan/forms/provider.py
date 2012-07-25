# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, FileField, TextAreaField, IntegerField, FloatField
from wtforms import validators
from custom_form import MultiCheckboxField, CustomForm
import util
from webapp2_extras.i18n import lazy_gettext as _
from forms import custom_filters


# Profile

class ProviderProfileForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'category', SelectField(_(u'Category'), choices=util.get_all_categories_for_profile_editing()))
        setattr(form, 'specialty', MultiCheckboxField(_(u'Specialties'), choices=util.getAllSpecialities()))
        setattr(form, 'bio', TextAreaField(_(u'Biography'), filters=[lambda x: custom_filters.escape_brackets(x)]))
        setattr(form, 'quote', TextAreaField(_(u'Quote'), filters=[lambda x: custom_filters.escape_brackets(x)]))
        setattr(form, 'associations', MultiCheckboxField(_(u'Organization Memberships'), choices=util.getAllAssociations()))
        setattr(form, 'certifications', MultiCheckboxField(_(u'Certifications'), choices=util.getAllCertifications()))
        setattr(form, 'practice_sites', MultiCheckboxField(_(u'Practice Sites'), choices=util.getAllSites()))
        setattr(form, 'spoken_languages', MultiCheckboxField(_(u'Spoken Languages'), choices=util.get_all_spoken_languages()))



# CV

class ProviderEducationForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'start_year', IntegerField(_(u'Start Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.'))]))
        setattr(form, 'end_year' , IntegerField(_(u'End Year'), description=_(u'Leave empty for present'), 
                                                validators=[validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.')), validators.Optional()]))
        setattr(form, 'school_name' , SelectField(_(u'School'), choices=util.get_all_schools()))   
        setattr(form, 'degree_type' , SelectField(_(u'Degree'), choices=util.get_all_degrees()))
        setattr(form, 'degree_title' , TextField(_(u'Degree Title')))
        setattr(form, 'description' , TextAreaField(_(u'Description'), filters=[custom_filters.escape_brackets]))

class ProviderExperienceForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'start_year', IntegerField(_(u'Start Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.'))]))
        setattr(form, 'end_year', IntegerField(_(u'End Year'), description=_(u'Leave empty for present'), 
                                                validators=[validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.')), validators.Optional()]))
        setattr(form, 'company_name', TextField(_(u'Company Name')))
        setattr(form, 'title', TextField(_(u'Position Title')))
        setattr(form, 'description', TextAreaField(_(u'Description'), filters=[custom_filters.escape_brackets]))

class ProviderContinuingEducationForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'year', IntegerField(_(u'Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.'))]))
        setattr(form, 'month', IntegerField(_(u'Month'), [validators.NumberRange(min=1, max=12, message=_(u'Please enter a valid month.')), validators.Optional()]))
        setattr(form, 'type', SelectField(_(u'Type'), choices=util.get_all_continuing_education_types()))    
        setattr(form, 'hours', FloatField(_(u'Hours'), [validators.NumberRange(min=0, max=1000, message=_(u'Please enter a valid number of hours.')), validators.Optional()]))
        setattr(form, 'title', TextField(_(u'Continuing Education Title')))
        setattr(form, 'description', TextAreaField(_(u'Description'), filters=[custom_filters.escape_brackets]))


# Photo

class ProviderPhotoForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'profile_photo', FileField(_(u'Upload')))



# Address

class ProviderAddressForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'title', SelectField(_(u'Title'), choices=util.get_all_titles()))
        setattr(form, 'first_name', TextField(_(u'First Name')))
        setattr(form, 'last_name', TextField(_(u'Last Name')))
        setattr(form, 'credentials', TextField(_(u'Credentials'), description=_('Letters that go after your name, ex: M.Sc. or M.D.')))
        setattr(form, 'phone', TextField(_(u'Telephone'), [validators.Optional(), validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212'))]))
        setattr(form, 'address', TextField(_(u'Addresse')))
        setattr(form, 'city', TextField(_(u'City')))
        setattr(form, 'postal_code', TextField(_(u'Postal Code'), [validators.Optional(), validators.Regexp(regex="^[a-zA-Z][0-9][a-zA-Z][0-9][a-zA-Z][0-9]$", message=_(u'Please make sure your postal code is in the following format: A1B2C3'))]))



# Admin only

class ProviderNoteForm(Form):
    body = TextAreaField(_(u'Note'))
    note_type = SelectField(_(u'Type'), choices=util.get_all_note_types())
    
class ProviderStatusForm(Form):
    status = SelectField(_(u'Status'), choices=util.get_all_status_types())
