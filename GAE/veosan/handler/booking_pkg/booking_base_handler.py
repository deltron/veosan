from handler.base import BaseHandler
from webapp2_extras.i18n import gettext as _

class BookingBaseHandler(BaseHandler):
    '''Common functions for all booking handlers'''
    
    @staticmethod
    def render_confirmed_patient(handler, patient, **kw):
        kw_new = { 'success_message' : _('You new appointment is confirmed!') }
        kw.update(kw_new)

        handler.patient.PatientBaseHandler.render_bookings(handler, patient, **kw)