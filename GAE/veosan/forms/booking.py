# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField
from wtforms import validators
from custom_form import CustomBooleanField
import util
from webapp2_extras.i18n import lazy_gettext as _
from utilities import time
from custom_form import CustomForm

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
        setattr(form, 'insurance', SelectField(_(u'Insurance'), choices=util.getAllInsurance()))
        # this should go into the booking object
        setattr(form, 'specialty', SelectField(_(u'Needs'), choices=util.getAllSpecialitiesForPatient()))
        setattr(form, 'comments', TextAreaField(_(u'Comments for your appointment')))