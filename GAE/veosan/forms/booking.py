# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField, HiddenField
from wtforms import validators
from custom_form import CustomBooleanField
import util
from webapp2_extras.i18n import lazy_gettext as _
from utilities import time
from custom_form import CustomForm
from forms import custom_validators

class SearchBookingForm(CustomForm):
    def _set_fields(self, form):
        setattr(form, 'category', SelectField(_(u'Category'), choices=util.get_all_categories()))
        setattr(form, 'location', SelectField(_(u'Location'), choices=util.get_all_regions()))
        setattr(form, 'homecare', CustomBooleanField(_(u'Receive care at home')))
        setattr(form, 'booking_date', SelectField(_(u'Date'), choices=time.getDatesList()))
        setattr(form, 'booking_time', SelectField(_(u'Time'), choices=time.get_time_list(), coerce=int))


class EmailOnlyBookingForm(Form):
    email = TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))])


class EmailAndAppointmentDetails(CustomForm):
    def _set_fields(self, form):
        setattr(form, 'email',TextField(_(u'E-mail Address'), [validators.Email(message=_(u'Invalid email address.'))]))
        setattr(form, 'telephone', TextField(_(u'Telephone'), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212'))]))
        setattr(form, 'specialty', SelectField(_(u'Needs'), choices=util.getAllSpecialitiesForPatient(),
                                               validators=[custom_validators.DisallowNoChoiceInSelect(message=_('Please choose an option from the list. If none of the options seems to fit, please choose "Other"'))]))
        setattr(form, 'comments', TextAreaField(_(u'Comments for your appointment')))
        setattr(form, 'insurance', SelectField(_(u'Insurance'), 
                                                   choices=util.getAllInsurance(),
                                                   validators=[custom_validators.DisallowNoChoiceInSelect(message=_('Please choose an option from the list. If none of the options seems to fit, please choose "Other"'))]
                                                   ))
        setattr(form, 'booking_date', HiddenField('booking_date'))
        setattr(form, 'booking_time', HiddenField('booking_time'))