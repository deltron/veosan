# -*- coding: utf-8 -*-

from custom_form import CustomForm
from forms import custom_validators
from webapp2_extras.i18n import lazy_gettext as _
from wtforms import TextField,  TextAreaField, validators


class AddCampaignForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'name', TextField(_(u'Campaign Name'), [validators.Length(min=2, message=_(u'Prospect ID required.')), custom_validators.UniqueCampaignName(message="Campaign name is not unique")]))
        
class EditCampaignForm(CustomForm):
    def _set_fields(self, form): 
        setattr(form, 'name', TextField(_(u'Name'), [validators.Length(min=2, message=_(u'Prospect ID required.'))]))
        setattr(form, 'description', TextField(_(u'Description')))
        setattr(form, 'subject_fr', TextField(_(u'Sujet Francais')))
        setattr(form, 'body_fr', TextAreaField(_(u'Body Francais')))
        setattr(form, 'subject_en', TextField(_(u'English Subject')))
        setattr(form, 'body_en', TextAreaField(_(u'English Body')))
        