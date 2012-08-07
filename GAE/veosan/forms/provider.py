# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, FileField, TextAreaField, IntegerField, FloatField, DateField
from wtforms import validators
from custom_form import MultiCheckboxField, CustomForm
import util
from utilities.time import get_days_of_the_week
from webapp2_extras.i18n import lazy_gettext as _
from forms import custom_filters, custom_validators


# Profile

class ProviderProfileForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'category', SelectField(_(u'Category'), choices=util.get_all_categories_for_profile_editing()))
        setattr(form, 'specialty', MultiCheckboxField(_(u'Specialties'), choices=util.getAllSpecialities()))
        setattr(form, 'bio', TextAreaField(_(u'Biography'), filters=[lambda x: custom_filters.escape_brackets(x)]))
        setattr(form, 'quote', TextAreaField(_(u'Quote'), filters=[lambda x: custom_filters.escape_brackets(x)]))
        setattr(form, 'practice_sites', MultiCheckboxField(_(u'Practice Sites'), choices=util.getAllSites()))
        setattr(form, 'spoken_languages', MultiCheckboxField(_(u'Spoken Languages'), choices=util.get_all_spoken_languages()))



# CV

class ProviderEducationForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'school_name', TextField(_(u'School'), 
                                               validators=[validators.Length(min=2, message=_(u'School name required.'))]))  
        setattr(form, 'location', TextField(_(u'Location')))

        setattr(form, 'start_year', IntegerField(_(u'Start Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.'))]))
        setattr(form, 'end_year' , IntegerField(_(u'End Year'), description=_(u'Leave empty for present'), 
                                                validators=[validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.')), validators.Optional()]))
        setattr(form, 'degree_type' , SelectField(_(u'Degree'), choices=util.get_all_degrees()))
        setattr(form, 'degree_title' , TextField(_(u'Degree Title')))
        setattr(form, 'description' , TextAreaField(_(u'Description'), filters=[custom_filters.escape_brackets]))

class ProviderExperienceForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'company_name', TextField(_(u'Organization Name')))
        setattr(form, 'location', TextField(_(u'Location')))
        setattr(form, 'title', TextField(_(u'Position Title')))

        setattr(form, 'start_year', IntegerField(_(u'Start Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.'))]))
        setattr(form, 'end_year', IntegerField(_(u'End Year'), description=_(u'Leave empty for present'), 
                                                validators=[validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.')), validators.Optional()]))
        setattr(form, 'description', TextAreaField(_(u'Description'), filters=[custom_filters.escape_brackets]))

class ProviderContinuingEducationForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'type', SelectField(_(u'Type'), choices=util.get_all_continuing_education_types()))    
        setattr(form, 'title', TextField(_(u'Continuing Education Title')))
        setattr(form, 'year', IntegerField(_(u'Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.'))]))
        setattr(form, 'month', IntegerField(_(u'Month'), [validators.NumberRange(min=1, max=12, message=_(u'Please enter a valid month.')), validators.Optional()]))
        setattr(form, 'hours', FloatField(_(u'Hours'), [validators.NumberRange(min=0, max=1000, message=_(u'Please enter a valid number of hours.')), validators.Optional()]))
        setattr(form, 'description', TextAreaField(_(u'Description'), filters=[custom_filters.escape_brackets]))

class ProviderOrganizationForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'organization', SelectField(_(u'Organization Name'), 
                                                  choices=util.get_all_organizations_for_form(),
                                                  validators=[custom_validators.DisallowNoChoiceInSelect(message=_('Please choose an option from the list. If none of the options seems to fit, please choose "Other" and write in the field below.'))]
                                            ))
        setattr(form, 'other', TextField(_(u'Other'), 
                                         description=_(u'Please enter the organization name here if not in the list'),
                                         validators=[custom_validators.RequiredIfOther('organization', message=_('Please enter an organization name'))]
                                    ))
        
        setattr(form, 'start_year', IntegerField(_(u'Start Year'), [validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.'))]))
        setattr(form, 'end_year', IntegerField(_(u'End Year'), description=_(u'Leave empty for present'), 
                                                validators=[validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.')), validators.Optional()]))

class ProviderCertificationForm(CustomForm):
    def _set_fields(self, form):        
        setattr(form, 'certification', SelectField(_(u'Certification Title'), 
                                                    choices=util.get_all_certifications_for_form(),
                                                    validators=[custom_validators.DisallowNoChoiceInSelect(message=_('Please choose an option from the list. If none of the options seems to fit, please choose "Other" and write in the field below.'))]
                                            ))
        setattr(form, 'other', TextField(_(u'Other'), 
                                         description=_(u'Please enter the certificate name here if not in the list'),
                                         validators=[custom_validators.RequiredIfOther('certification', message=_('Please enter a certificate name'))]
                                    ))
        setattr(form, 'year', IntegerField(_(u'Year Obtained'), [validators.NumberRange(min=1940, max=2100, message=_(u'Please enter a valid year.'))]))


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
        setattr(form, 'phone', TextField(_(u'Telephone'), [validators.Optional(), validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212'))]))
        setattr(form, 'address', TextField(_(u'Addresse')))
        setattr(form, 'city', TextField(_(u'City')))
        setattr(form, 'province', SelectField(_(u'Province'), choices=util.get_all_provinces_sorted()))
        setattr(form, 'postal_code', TextField(_(u'Postal Code'), [validators.Optional(), validators.Regexp(regex="^[a-zA-Z][0-9][a-zA-Z][0-9][a-zA-Z][0-9]$", message=_(u'Please make sure your postal code is in the following format: A1B2C3'))]))

class ProviderScheduleForm(CustomForm):
    def _set_fields(self, form):        
        #setattr(form, 'day', SelectField(_(u'Day'), choices=get_days_of_the_week()))
        setattr(form, 'day', IntegerField(_(u'Day')))
        setattr(form, 'start_time', IntegerField(_(u'Start Time')))
        setattr(form, 'end_time', IntegerField(_(u'End Time')))

# Admin only

class ProviderNoteForm(Form):
    body = TextAreaField(_(u'Note'))
    note_type = SelectField(_(u'Type'), choices=util.get_all_note_types())
    event_date = DateField(_(u'Date'))
    
class ProviderStatusForm(Form):
    status = SelectField(_(u'Status'), choices=util.get_all_status_types())
