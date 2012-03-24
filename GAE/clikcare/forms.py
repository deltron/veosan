from wtforms import Form, TextField, SelectField, SelectMultipleField, FileField, validators, widgets
import util

# WTF! WTF doesn't come with checkboxes out of the box
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
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


class ProviderAddressForm(Form):
    profilePhoto = FileField('T&eacute;l&eacute;charger')
    firstName = TextField('Pr&eacute;nom', [validators.Length(min=1, message='Pr&eacute;nom requis.')])
    lastName = TextField('Nom', [validators.Length(min=1, message='Nom requis.')])
    email = TextField('Courriel', [validators.Email(message='Addresse de courriel invalide.')])
    telephone = TextField('T&eacute;l&eacute;phone', [validators.Regexp(regex="^[2-9]\d{2}-\d{3}-\d{4}$", message='Format 514-555-1212')])
    regions = SelectField('Lieu', choices=util.getAllRegions())
    address = TextField('Addresse', [validators.Length(min=10, message='Address requis.')])
    city = TextField('Ville', [validators.Length(min=10, message='Address requis.')])
    postalCode = TextField('Code Postal', [validators.Length(min=6, message='Address requis.')])

class ProviderProfileForm(Form):
    categories = SelectField('Cat&eacute;gorie', choices=util.getAllCategories())
    specialties = MultiCheckboxField('Sp&eacute;cialit&eacute;s', choices=util.getAllSpecialities())
    schools = SelectField('&Eacute;cole', choices=util.getAllSchools())
    degree = MultiCheckboxField('Diplome(s)', choices=util.getAllDiplomas())
    startYear = TextField('En pratique depuis', [validators.Length(min=4, max=4, message='Requis.')])
