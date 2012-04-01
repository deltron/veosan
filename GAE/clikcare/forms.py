# -*- coding: utf-8 -*-

from wtforms import Form, Field, TextField, SelectField, SelectMultipleField, FileField, BooleanField
from wtforms import validators, widgets
from cgi import escape
import util

''' 
need to write our own list widget so the <label> doesn't appear after
the checkbox (which shows up on a new line and also makes the click target
much smaller). 

Bottom line: default behavior for checkboxes from WTForms makes no sense

'''
# TODO code in some kind of handling for default options

class MultipleCheckboxWidget(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
 
        html = []

        for subfield in field:
            if subfield.data in field.default:
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


  
class BookingForm(Form):
    email = TextField(_(u'E-mail Address').decode("UTF-8"), [validators.Email(message=_(u'Invalid email address.').decode("UTF-8"))])
    categories = SelectField(_(u'Category').decode("UTF-8"), choices=util.getAllCategories())
    regions = SelectField(_(u'Location').decode("UTF-8"), choices=util.getAllRegions())
    dates = SelectField(_(u'Date').decode("UTF-8"), choices=util.getDatesList())
    times = SelectField(_(u'Time').decode("UTF-8"), choices=util.getTimesList())


class PatientForm(Form):
    firstName = TextField(_(u'First Name'), [validators.Length(min=1, message='Pr&eacute;nom requis.')])
    lastName = TextField(_(u'Last Name'), [validators.Length(min=1, message='Nom requis.')])
    email = TextField(_(u'E-mail Address'), [validators.Email(message='Addresse de courriel invalide.')])
    telephone = TextField(_(u'Telephone'), [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message='Format 514-555-1212')])
    insurance = SelectField(_(u'Insurance'), choices=util.getAllInsurance())
    confirmation = MultiCheckboxField(_(u'Confirmation'), choices=util.getAllConfirmation(), default=['email']) #default not implemented
    #booking = TextField('', widget=HiddenInput())


class ProviderAddressForm(Form):
    firstName = TextField('firstName', [validators.Length(min=1, message='Pr&eacute;nom requis.')])
    lastName = TextField('lastName', [validators.Length(min=1, message='Nom requis.')])
    email = TextField('email', [validators.Email(message='Addresse de courriel invalide.')])
    phone = TextField('T&eacute;l&eacute;phone', [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message='Format 514-555-1212')])
    region = SelectField('Lieu', choices=util.getAllRegions())
    address = TextField('Addresse', [validators.Length(min=5, message='Address requis.')])
    city = TextField('Ville', [validators.Length(min=3, message='Address requis.')])
    postalCode = TextField('Code Postal', [validators.Length(min=6, message='Address requis.')])
    #key = TextField('key')
    
class ProviderPhotoForm(Form):
    profilePhoto = FileField('T&eacute;l&eacute;charger')

class ProviderProfileForm(Form):
    categoriy = SelectField(_(u'Category'), choices=util.getAllCategories())
    specialty = MultiCheckboxField(_(u'Specialties'), choices=util.getAllSpecialities())
    school = SelectField(_(u'School'), choices=util.getAllSchools())
    degree = MultiCheckboxField(_(u'Diploma'), choices=util.getAllDiplomas())
    startYear = TextField(_(u'Member of order since'), [validators.Length(min=2, max=4, message='Your first year of practice')])
    homeVisits = CustomBooleanField(_(u'I am willing to do on-site visits'))
    #key = TextField('key')
