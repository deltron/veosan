# -*- coding: utf-8 -*-
from wtforms import Form, TextField, SelectField, SelectMultipleField, FileField, validators, widgets, HiddenField, IntegerField
import util


''' 
need to write our own list widget so the <label> doesn't appear after
the checkbox (which shows up on a new line and also makes the click target
much smaller). 

Bottom line: default behavior for checkboxes from WTForms makes no sense

'''
class CheckboxWidget(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []

        for subfield in field:
            html.append(u'<label %s>%s %s</label>' % (widgets.html_params(**kwargs), unicode(subfield), unicode(subfield.label.text)))
        return widgets.HTMLString(u''.join(html))


# WTF! WTF doesn't come with checkboxes out of the box
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = CheckboxWidget()
    option_widget = widgets.CheckboxInput()
    
    
    

class BookingForm(Form):
    email = TextField('Courriel', [validators.Email(message='Addresse de courriel invalide.')])
    categories = SelectField('Cat&eacute;gorie', choices=util.getAllCategories())
    regions = SelectField('Lieu', choices=util.getAllRegions())
    dates = SelectField('Date', choices=util.getDatesList())
    times = SelectField('Heure', choices=util.getTimesList())


class PatientForm(Form):
    firstName = TextField('Pr&eacute;nom', [validators.Length(min=1, message='Pr&eacute;nom requis.')])
    lastName = TextField('Nom', [validators.Length(min=1, message='Nom requis.')])
    email = TextField('Courriel', [validators.Email(message='Addresse de courriel invalide.')])
    telephone = TextField('T&eacute;l&eacute;phone', [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message='Format 514-555-1212')])
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
    categoriy = SelectField('Cat&eacute;gorie', choices=util.getAllCategories())
    specialty = MultiCheckboxField('Sp&eacute;cialit&eacute;s', choices=util.getAllSpecialities())
    school = SelectField('&Eacute;cole', choices=util.getAllSchools())
    degree = MultiCheckboxField('Diplome(s)', choices=util.getAllDiplomas())
    startYear = TextField('En pratique depuis', [validators.Length(min=2, max=4, message='Your first year of practice')])
    #key = TextField('key')
