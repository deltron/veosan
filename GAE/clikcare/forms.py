# -*- coding: utf-8 -*-

from wtforms import Form, Field, TextField, SelectField, SelectMultipleField, FileField, BooleanField, PasswordField, HiddenField, TextAreaField
from wtforms import validators, widgets
from cgi import escape
import util

''' 
need to write our own list widget so the <label> doesn't appear after
the checkbox (which shows up on a new line and also makes the click target
much smaller). 

Bottom line: default behavior for checkboxes from WTForms makes no sense

'''
class MultipleCheckboxWidget(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
 
        html = []

        for subfield in field:
            if field.default is not None and subfield.data in field.default:
                subfield.checked = True

            html.append(u'<label %s>%s %s</label>' % (widgets.html_params(**kwargs), unicode(subfield), unicode(subfield.label.text)))
        return widgets.HTMLString(u''.join(html))

class CustomCheckboxInput(widgets.Input):
    input_type = 'checkbox'
    
    html_params = staticmethod(widgets.html_params)

    def __call__(self, field, **kwargs):
        if getattr(field, 'checked', field.data):
            kwargs['checked'] = True

        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
            
        label_class = u' '
        if 'class' in kwargs:
            label_class = (u'%s="%s"' % (unicode('class'), escape(unicode(kwargs['class']), quote=True)))

        return widgets.HTMLString(u'<label %s><input %s> %s</label>' % (label_class, widgets.html_params(name=field.name, **kwargs), field.label.text))


# WTF! WTF doesn't come with checkboxes out of the box
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = MultipleCheckboxWidget()
    option_widget = widgets.CheckboxInput()
    

# Custom boolean field that shows up as :
#   [] Boolean field label
# 
# instead of the default behavior from WTForms which is
#   Boolean field label []
class CustomBooleanField(BooleanField):
    """
    Represents an ``<label><input type="checkbox"> label text</label>``.
    """
    widget = CustomCheckboxInput()

    def _value(self):
        ''' overwrite default value for true from y to True '''
        
        if self.raw_data:
            return unicode(self.raw_data[0])
        else:
            return u'True'

  
class BookingForm(Form):
    #email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    bookingCategory = SelectField(_(u'Category').decode("UTF-8"), choices=util.getAllCategories())
    bookingRegion = SelectField(_(u'Location').decode("UTF-8"), choices=util.getAllRegions())
    bookingDate = SelectField(_(u'Date').decode("UTF-8"), choices=util.getDatesList())
    bookingTime = SelectField(_(u'Time').decode("UTF-8"), choices=util.getTimesList())

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

    
class ProviderAddressForm(Form):
    prefix = TextField(_(u'Prefix').decode("UTF-8"))
    first_name = TextField(_(u'First Name').decode("UTF-8"), [validators.Length(min=1, message=_(u'First name is a required field').decode("UTF-8"))])
    last_name = TextField(_(u'Last Name').decode("UTF-8"), [validators.Length(min=1, message=_(u'Last name is a required field').decode("UTF-8"))])
    postfix = TextField(_(u'Postfix qualifications').decode("UTF-8"))
    email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    phone = TextField(_(u'Telephone').decode("UTF-8"), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message=_(u'Please make sure phone number is in the following format: 514-555-1212').decode("UTF-8"))])
    region = SelectField(_(u'Location').decode("UTF-8"), choices=util.getAllRegions())
    address = TextField('Addresse', [validators.Length(min=5, message='Address requis.')])
    city = TextField('Ville', [validators.Length(min=3, message='Address requis.')])
    postal_code = TextField('Code Postal', [validators.Length(min=6, message='Address requis.')])
    #key = TextField('key')
    
class ProviderPhotoForm(Form):
    profilePhoto = FileField('T&eacute;l&eacute;charger')

class ProviderProfileForm(Form):
    category = SelectField(_(u'Category').decode("UTF-8"), choices=util.getAllCategories())
    specialty = MultiCheckboxField(_(u'Specialties').decode("UTF-8"), choices=util.getAllSpecialities())
    start_year = TextField(_(u'Active Since').decode("UTF-8"), [validators.Length(min=4, max=4, message='Your first year of practice')])
    bio = TextAreaField(_('Biography').decode("UTF-8"))
    quote = TextAreaField(_(u'Quote').decode("UTF-8"))
    associations = MultiCheckboxField(_(u'Associations').decode("UTF-8"), choices=util.getAllAssociations())
    certifications = MultiCheckboxField(_(u'Certifications').decode("UTF-8"), choices=util.getAllCertifications())
    onsite = CustomBooleanField(_(u'I am willing to do on-site visits').decode("UTF-8"))

    #key = TextField('key')
    
class ProviderTermsForm(Form):
    # terms agreement (required)
    terms_agreement = CustomBooleanField(_(u'I agree with the Terms of Service').decode("UTF-8"), [validators.Required(message=_(u'You must accept the terms to register').decode("UTF-8"))])
    # todo validate against exact first_name, last_name string
    #signature = TextField(_(u'Signature').decode("UTF-8"), [validators.Length(min=5, message='First name and last name as in address page')])

class ProviderLoginForm(Form):
    email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    password = PasswordField('Password')

class ContactForm(Form):
    email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    subject = TextField(_(u'Subject').decode("UTF-8"), [validators.Length(min=3, message='Subject required.')])
    message = TextAreaField(_(u'Message').decode("UTF-8"))
    
class LoginForm(Form):
    email = TextField(_(u'Email').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    password = PasswordField(_(u'Password').decode("UTF-8"), [validators.Length(min=6, message='Password needs at least 6 characters')])
    remember_me = CustomBooleanField(_(u'Remember Me').decode("UTF-8"))
