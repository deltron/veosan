# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField, PasswordField, TextAreaField
from wtforms import validators
from custom_form import CustomBooleanField
import util

  
class BookingForm(Form):
    category = SelectField(_(u'Category').decode("UTF-8"), choices=util.getAllCategories())
    location = SelectField(_(u'Location').decode("UTF-8"), choices=util.getAllRegions())
    booking_date = SelectField(_(u'Date').decode("UTF-8"), choices=util.getDatesList())
    booking_time = SelectField(_(u'Time').decode("UTF-8"), choices=util.getTimesList())

class EmailOnlyBookingForm(Form):
    email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])

class PatientForm(Form):
    first_name = TextField(_(u'First Name').decode("UTF-8"), [validators.Length(min=1, message=_(u'First name is a required field').decode("UTF-8"))])
    last_name = TextField(_(u'Last Name').decode("UTF-8"), [validators.Length(min=1, message=_(u'Last name is a required field').decode("UTF-8"))])
    email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    password = PasswordField(_(u'Password').decode("UTF-8"), [validators.Length(min=6, message='Password needs at least 6 characters')])
    telephone = TextField(_(u'Telephone').decode("UTF-8"), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212').decode("UTF-8"))])
    insurance = SelectField(_(u'Insurance').decode("UTF-8"), choices=util.getAllInsurance())
    # this should go into the booking object
    specialty = SelectField(_(u'Needs').decode("UTF-8"), choices=util.getAllSpecialitiesForPatient())
    comments = TextAreaField(_(u'Comments for your appointment').decode("UTF-8"))
    # terms agreement (required)
    terms_agreement = CustomBooleanField(_(u'I agree with the Terms of Service').decode("UTF-8"), [validators.Required(message=_(u'You must accept the terms to book an appointment').decode("UTF-8"))])
    
    
# to simplify for now, just assume email-only confirmation
#   confirmation = MultiCheckboxField(_(u'Confirmation').decode("UTF-8"), choices=util.getAllConfirmation(), default=['email'])


class ContactForm(Form):
    email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    subject = TextField(_(u'Subject').decode("UTF-8"), [validators.Length(min=3, message='Subject required.')])
    message = TextAreaField(_(u'Message').decode("UTF-8"))
