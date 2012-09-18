from wtforms import Form, TextField, SelectField, TextAreaField
from wtforms import validators
from custom_form import CustomForm
import util
from webapp2_extras.i18n import lazy_gettext as _
from forms import custom_validators


class ProspectStatusForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'status', SelectField(_(u'Status'), choices=util.get_all_prospect_status_types()))
    
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
        setattr(form, 'body', TextAreaField(_(u'Note')))