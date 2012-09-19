from wtforms import Form, TextField, SelectField, TextAreaField
from wtforms import validators
from custom_form import CustomForm
import util
from webapp2_extras.i18n import lazy_gettext as _
from forms import custom_validators
from forms.custom_form import MultiCheckboxField
from wtforms.ext.dateutil.fields import DateField
import datetime


class ProspectTagsForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'tags', MultiCheckboxField(_(u'Tags'), choices=util.get_all_prospect_tags()))
    
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

class ProspectNoteForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'note_type', SelectField(_(u'Type'), choices=util.get_all_note_types()))
        setattr(form, 'event_date', DateField(_(u'Event Date'), default=datetime.datetime.now()))
        setattr(form, 'body', TextAreaField(_(u'Note')))