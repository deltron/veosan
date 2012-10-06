from handler.auth import patient_required
from forms.provider import ProviderAddressForm
from google.appengine.ext import ndb
from handler.base import BaseHandler

class PatientEditAddressHandler(BaseHandler):
    @patient_required
    def get(self, patient_key=None):
        patient = ndb.Key(urlsafe=patient_key).get()
        address_form = ProviderAddressForm().get_form(obj=patient)

        self.render_template('patient/address.html', patient=patient, address_form=address_form)

    @patient_required
    def post(self, patient_key=None):
        address_form = ProviderAddressForm().get_form(self.request.POST)
        
        if address_form.validate():
            # Store Provider
            patient = ndb.Key(urlsafe=patient_key).get()
            
            address_form.populate_obj(patient)
            patient.put()

            self.render_template('patient/address.html', patient=patient, address_form=address_form)

        else:
            # show validation error
            patient = ndb.Key(urlsafe=patient_key).get()

            self.render_template('patient/address.html', patient=patient, address_form=address_form)