
import logging, urlparse
from google.appengine.api import mail
from webapp2_extras.i18n import gettext as _
import util
import traceback

VEOSAN_SUPPORT_ADDRESS = 'support@veosan.com'

def email_error_log_report(error_logs):
    message = mail.EmailMessage()
    message.sender = "Veosan Support" + ' <' + VEOSAN_SUPPORT_ADDRESS + '>'
    message.to = "Veosan Support" + ' <' + VEOSAN_SUPPORT_ADDRESS + '>'
    message.subject = "Error Log Report"
    
    message.body = error_logs
    
    try:
        logging.info('Sending error_log to support')
        message.send()
    except Exception as e:
        logging.error('Email not sent. %s' % e)


def email_exception_report(request, exception):
    message = mail.EmailMessage()
    message.sender = "Veosan Support" + ' <' + VEOSAN_SUPPORT_ADDRESS + '>'
    message.to = "Veosan Support" + ' <' + VEOSAN_SUPPORT_ADDRESS + '>'
    message.subject = "Exception Report: " + str(exception)
    
    message.body = "T R A C E B A C K\n"
    message.body += "=================\n\n"
    message.body += traceback.format_exc(exception)
    message.body += "\n\n\n\n"
    message.body += "R E Q U E S T D U M P\n"
    message.body += "=====================\n\n"
    message.body += str(request)
    
    try:
        logging.info('Sending traceback to support')
        message.send()
    except Exception as e:
        logging.error('Email not sent. %s' % e)

def render_booking_email_body(jinja2, template_filename, booking, activation_url=None, **kw):

    
    kw = {'booking': booking, 'provider': booking.provider.get(), 'patient': booking.patient.get(), 'activation_url': activation_url}
    kw['certification_dict'] = dict(util.getAllCertifications())

    
    return jinja2.render_template(template_filename, **kw)
    


def email_booking_to_patient(handler, booking, activation_url=None):
    ''' send booking info to patient, provider and us '''
    patient = booking.patient.get()
    provider = booking.provider.get()
    to_address = patient.email
    # check email valid
    if not mail.is_email_valid(to_address):
        logging.warn('Email is not valid: %s -- trying anyway...' % to_address)
        
    # create message
    message = mail.EmailMessage()
    message.sender = "Veosan" + ' <' + VEOSAN_SUPPORT_ADDRESS + '>'
    message.to = to_address
    category_label = dict(util.get_all_categories_all_domains())[provider.category]
    message.subject = '%s - %s' % (_(u'Veosan Appointment'), _(category_label).capitalize())
    
    kw = {'booking': booking, 'activation_url': activation_url}
    logging.debug('activation url for email: %s' % activation_url)
    message.body = render_booking_email_body(handler.jinja2, 'email/patient_booking.txt', **kw)
    
    try:
        logging.info('Sending booking email to provider %s' % patient.email)
        message.send()
        
        booking.email_sent_to_patient = True
        booking.put()
    except Exception as e:
        logging.error('Email to patient not sent. %s' % e)


def email_booking_to_provider(handler, booking):
    ''' 
        Send confirmed booking to provider
    '''
    patient = booking.patient.get()
    provider = booking.provider.get()
    to_address = provider.email
    # create message
    message = mail.EmailMessage()
    message.sender = "Veosan" + ' <' + VEOSAN_SUPPORT_ADDRESS + '>'
    message.to = to_address
    message.subject = '%s - %s %s %s' % ('Veosan', _('New Appointment with'), patient.first_name, patient.last_name)
    # booking admin url
    url_obj = urlparse.urlparse(handler.request.url)
    provider_bookings_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/provider/bookings/' + provider.vanity_url, '', '', ''))
    message.body = render_booking_email_body(handler.jinja2, 'email/provider_booking.txt', booking=booking, provider_bookings_url=provider_bookings_url)
    try:
        logging.info('Sending booking email to patient %s' % patient.email)
        message.send()

        booking.email_sent_to_provider = True
        booking.put()
    except Exception as e:
        logging.error('Email to patient not sent. %s' % e)
        
        

def email_user_password_reset(jinja2, user, activation_url):
    ''' Send password reset email to provider '''
    message = mail.EmailMessage()
    message.sender = VEOSAN_SUPPORT_ADDRESS
    message.to = user.get_email()
    message.subject = u'Veosan - ' + _('Password reset instructions')
    message.body = jinja2.render_template('email/provider_passwordreset.txt', activation_url=activation_url)
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        

def email_invite(jinja2, invite, invite_url):
    ''' Send invitation email '''
    from_provider = invite.provider.get()
    
    message = mail.EmailMessage()
    message.sender = from_provider.first_name + " " + from_provider.last_name + " <" + VEOSAN_SUPPORT_ADDRESS + ">"
    message.reply_to = from_provider.email
    message.to = invite.email
    message.subject = u'Invitation to join Veosan from %s %s' % (from_provider.first_name, from_provider.last_name)
    
    message.body = jinja2.render_template('email/invite.txt', invite=invite, invite_url=invite_url)
    
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)


def email_connect_request(jinja2, from_provider, target_provider, accept_url):
    ''' Send invitation email '''
    
    message = mail.EmailMessage()
    message.sender = from_provider.first_name + " " + from_provider.last_name + " <" + VEOSAN_SUPPORT_ADDRESS + ">"
    message.reply_to = from_provider.email
    message.to = target_provider.email
    message.subject = u'Join my network on Veosan!'
    
    message.body = jinja2.render_template('email/connect_request.txt', from_provider=from_provider, target_provider=target_provider, accept_url=accept_url)
    
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        

def email_provider_welcome(jinja2, provider):
    ''' Send welcome email '''
    
    message = mail.EmailMessage()
    message.sender = "David Leblanc <" + VEOSAN_SUPPORT_ADDRESS + ">"
    message.to = provider.email
    message.bcc = VEOSAN_SUPPORT_ADDRESS
    message.subject = provider.first_name + _(', welcome to Veosan!')
    
    message.body = jinja2.render_template('email/provider_welcome.txt', provider=provider)
    
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)

def email_contact_form(jinja2, from_email, subject, message_body):
    logging.info('Feedback from %s | subject: %s\n\nMESSAGE\n=========\n%s' % (from_email, subject, message_body))
    
    message_body = "From: %s\n\n\n%s" % (from_email, message_body)
    
    message = mail.EmailMessage()
    message.sender = VEOSAN_SUPPORT_ADDRESS
    message.to = VEOSAN_SUPPORT_ADDRESS
    message.subject = subject
    message.body = message_body
    
    try:
        message.send()
    except Exception as e:
        logging.error('Email to provider not sent. %s' % e)
        raise e
