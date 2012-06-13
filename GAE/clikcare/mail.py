
import logging
from google.appengine.api import mail
from webapp2_extras.i18n import gettext as _
import util

CLIK_SUPPORT_ADDRESS = 'cliktester@gmail.com'


def render_booking_email_body(jinja2, template_filename, booking, activation_url=None):
    tv = {'b': booking, 'provider': booking.provider.get(), 'patient': booking.patient.get(), 'activation_url': activation_url}
    return jinja2.render_template(template_filename, **tv)
    


def email_booking_to_patient(jinja2, booking, activation_url=None):
    ''' send booking info to patient, provider and us '''
    patient = booking.patient.get()
    provider = booking.provider.get()
    to_address = patient.email
    # check email valid
    if not mail.is_email_valid(to_address):
        logging.warn('Email is not valid: {0}. Trying anyway...' %  to_address)
    # create message
    message = mail.EmailMessage()
    message.sender = CLIK_SUPPORT_ADDRESS
    message.to = to_address
    category_label = dict(util.getAllCategories())[provider.category]
    message.subject = u'Cliksoin Reservation - %s' % _(category_label).capitalize()
    tv = {'booking': booking, 'activation_url': activation_url}
    message.body = render_booking_email_body(jinja2, 'email/patient_booking.txt', **tv)
    try:
        message.send()
    except Exception as e:
        logging.error('Email to patient not sent. %s' % e)



def emailSolicitProvider(jinja2, provider, activation_url):
    ''' Send solicitation email to provider '''
    message = mail.EmailMessage()
    message.sender = CLIK_SUPPORT_ADDRESS
    message.to = provider.email
    message.subject = u'Cliksoin - Please confirm your profile %s' % provider.fullName()
    tv = {'provider': provider, 'activation_url': activation_url}
    message.body = jinja2.render_template('email/provider_solicit.txt', **tv)
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        
def emailProviderPasswordReset(jinja2, provider, activation_url):
    ''' Send solicitation email to provider '''
    message = mail.EmailMessage()
    message.sender = CLIK_SUPPORT_ADDRESS
    message.to = provider.email
    message.subject = u'Cliksoin - Password Reset Instructions for %s' % provider.fullName()
    tv = {'provider': provider, 'activation_url': activation_url}
    message.body = jinja2.render_template('email/provider_passwordreset.txt', **tv)
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        
        
def emailProviderWelcomeMessage(jinja2, provider):
    pass

def email_contact_form(jinja2, from_email, subject, message_body):
    logging.info('Feedback from %s | subject: %s\n\nMESSAGE\n=========\n%s' % (from_email, subject, message_body))
    
    message = mail.EmailMessage()
    message.sender = from_email
    message.to = CLIK_SUPPORT_ADDRESS
    message.subject = subject
    message.body = message_body
    
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        raise e
