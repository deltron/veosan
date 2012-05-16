
import logging
from babel import Locale
from base import lang
from google.appengine.api import mail

CLIK_SUPPORT_ADDRESS = 'philippe.caya@gmail.com'


def renderBookingEmailBody(jinja2, template_filename, booking):
    tv = {'b': booking, 'provider': booking.provider, 'patient': booking.patient}
    return jinja2.render_template(template_filename, **tv)
    

def emailBookingToPatient(jinja2, booking):
    ''' send booking info to patient, provider and us '''
    to_address = booking.patient.email
    # check email valid
    if not mail.is_email_valid(to_address):
        logging.warn('Email is not valid: {0}. Trying anyway...' %  to_address)
    # create message
    message = mail.EmailMessage()
    message.sender = CLIK_SUPPORT_ADDRESS
    message.to = to_address
    message.subject = u'Cliksoin Reservation - %s' % _(booking.provider.category).decode("UTF-8").capitalize()
    message.body = renderBookingEmailBody(jinja2, 'email/patient_booking.txt', booking)
    try:
        message.send()
    except Exception as e:
        logging.error('Email to patient not sent. %s' % e)



def emailSolicitProvider(jinja2, provider, activation_url):
    ''' Send solicitation email to provider '''
    message = mail.EmailMessage()
    message.sender = CLIK_SUPPORT_ADDRESS
    message.to = provider.email
    message.subject = u'Cliksoin - Confirm your profile %s' % provider.fullName()
    tv = {'p': provider, 'activation_url': activation_url}
    message.body = jinja2.render_template('email/provider_solicit.txt', **tv)
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        
        