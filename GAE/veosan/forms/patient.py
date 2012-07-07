# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField
from wtforms import validators
from custom_form import CustomBooleanField
import util
from webapp2_extras.i18n import lazy_gettext as _

class PatientForm(Form):
    first_name = TextField(_(u'First Name'), [validators.Length(min=1, message=_(u'First name is a required field'))])
    last_name = TextField(_(u'Last Name'), [validators.Length(min=1, message=_(u'Last name is a required field'))])
    telephone = TextField(_(u'Telephone'), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212'))])
    address = TextField(_(u'Addresse'), [validators.Length(min=5, message='Address requis.')])
    city = TextField(_(u'City'), [validators.Length(min=3, message='Address requis.')])
    postal_code = TextField(_(u'Postal Code'), [validators.Length(min=6, message='Address requis.')])
    
    insurance = SelectField(_(u'Insurance'), choices=util.getAllInsurance())
    # this should go into the booking object
    specialty = SelectField(_(u'Needs'), choices=util.getAllSpecialitiesForPatient())
    comments = TextAreaField(_(u'Comments for your appointment'))
    # terms agreement (required)
    terms_agreement = CustomBooleanField(_(u'I agree with the Terms of Service'), [validators.Required(message=_(u'You must accept the terms to book an appointment'))])
