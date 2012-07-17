
import logging
from google.appengine.api import mail
from webapp2_extras.i18n import gettext as _
import util

VEOSAN_SUPPORT_ADDRESS = 'support@veosan.com'


def render_booking_email_body(jinja2, template_filename, booking, activation_url=None):
    kw = {'b': booking, 'provider': booking.provider.get(), 'patient': booking.patient.get(), 'activation_url': activation_url}
    return jinja2.render_template(template_filename, **kw)
    


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
    message.sender = VEOSAN_SUPPORT_ADDRESS
    message.to = to_address
    category_label = dict(util.get_all_categories())[provider.category]
    message.subject = u'veosan reservation - %s' % _(category_label).capitalize()
    kw = {'booking': booking, 'activation_url': activation_url}
    message.body = render_booking_email_body(jinja2, 'email/patient_booking.txt', **kw)
    try:
        message.send()
    except Exception as e:
        logging.error('Email to patient not sent. %s' % e)



def emailSolicitProvider(jinja2, provider, activation_url):
    ''' Send solicitation email to provider '''
    message = mail.EmailMessage()
    message.sender = 'Veosan <' + VEOSAN_SUPPORT_ADDRESS + '>'
    message.to = provider.email
    message.subject = u'Veosan Account Activation'
    kw = {'provider': provider, 'activation_url': activation_url}
    message.body = jinja2.render_template('email/provider_solicit.txt', **kw)
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        
def email_user_password_reset(jinja2, user, activation_url):
    ''' Send solicitation email to provider '''
    message = mail.EmailMessage()
    message.sender = VEOSAN_SUPPORT_ADDRESS
    message.to = user.get_email()
    message.subject = u'Veosan - password reset instructions'
    message.body = jinja2.render_template('email/provider_passwordreset.txt', activation_url=activation_url)
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
    message.to = VEOSAN_SUPPORT_ADDRESS
    message.subject = subject
    message.body = message_body
    
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        raise e
