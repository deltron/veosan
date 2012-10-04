from wtforms import Form, TextField, SelectField, TextAreaField
from wtforms import validators
from custom_form import CustomForm
import util
from data import db
from webapp2_extras.i18n import lazy_gettext as _
from forms import custom_validators
from forms.custom_form import MultiCheckboxField
from wtforms.ext.dateutil.fields import DateField, DateTimeField
import datetime
from pytz import tzinfo


class ProspectTagsForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'tags', MultiCheckboxField(_(u'Tags'), choices=util.get_all_prospect_tags()))

class ProspectEmploymentTagsForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'employment_tags', MultiCheckboxField(_(u'Employment'), choices=util.get_all_employment_tags()))

    
class ProviderProspectForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'prospect_id', TextField(_(u'Prospect ID'), [validators.Length(min=2, message=_(u'Prospect ID required.')), custom_validators.UniqueProspectID(message="Prospect ID is not unique")]))
        setattr(form, 'language', SelectField(_(u'Language'), choices=util.get_all_profile_languages()))
        setattr(form, 'email', TextField(_(u'Prospect Email'), [validators.Length(min=2, message=_(u'Email required.'))]))
        setattr(form, 'first_name', TextField(_(u'First Name'), [validators.Length(min=2, message=_(u'Email required.'))]))
        setattr(form, 'last_name', TextField(_(u'Last Name'), [validators.Length(min=2, message=_(u'Email required.'))]))
        setattr(form, 'category', SelectField(_(u'Category'), choices=util.get_all_categories_for_profile_editing(),
                                              validators=[custom_validators.DisallowNoChoiceInSelect(message=_('Please choose an option from the list. If none of the options seems to fit, please choose "Other"'))]
                                              ))

class ProviderProspectEditForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'language', SelectField(_(u'Language'), choices=util.get_all_profile_languages()))
        setattr(form, 'email', TextField(_(u'Prospect Email'), [validators.Length(min=2, message=_(u'Email required.'))]))
        setattr(form, 'phone', TextField(_(u'Phone')))
        setattr(form, 'first_name', TextField(_(u'First Name'), [validators.Length(min=2, message=_(u'Email required.'))]))
        setattr(form, 'last_name', TextField(_(u'Last Name'), [validators.Length(min=2, message=_(u'Email required.'))]))
        setattr(form, 'category', SelectField(_(u'Category'), choices=util.get_all_categories_for_profile_editing(),
                                              validators=[custom_validators.DisallowNoChoiceInSelect(message=_('Please choose an option from the list. If none of the options seems to fit, please choose "Other"'))]
                                              ))

class ProviderProspectSearchForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'search', TextField(_(u'Search')))

class ProspectNoteForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'note_type', SelectField(_(u'Type'), choices=util.get_all_note_types()))
        setattr(form, 'event_date', DateTimeField(_(u'Event Date'), default=datetime.datetime.now()))
        setattr(form, 'body', TextAreaField(_(u'Note')))
        
        
def get_campaign_choices():
    campaigns = db.fetch_campaigns()
    campaign_choices = map(lambda c: (c.key.urlsafe(), c.name), campaigns)
    return campaign_choices

class ProspectAddToCampaignForm(CustomForm):
    def _set_fields(self, form):
        setattr(form, 'campaign', SelectField(_(u'Add to Campaign'), choices=get_campaign_choices()))
        