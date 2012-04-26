
import logging
from babel import Locale
from base import lang
from google.appengine.api import mail
import datetime

CLIK_SUPPORT_ADDRESS = 'philippe.caya@gmail.com'

def emailBooking(booking):
    ''' send booking info to patient, provider and us '''
    patient = booking.patient
    provider = booking.provider
    category = provider.category
    to_address = patient.email
    # check email valid
    if not mail.is_email_valid(to_address):
        logging.warn('Email is not valid: {0}. Trying anyway...' %  to_address)
    # create message
    message = mail.EmailMessage()
    message.sender = CLIK_SUPPORT_ADDRESS
    message.to = to_address
    message.subject = u'Cliksoin Reservation - %s' % _(category).decode("UTF-8").capitalize()
    message.body = '''
Your are booked for {0} with {1} on {2}

{3}
    '''.format(_(category), provider.fullName(), booking.dateTime, booking.__dict__)
    # send message
    message.send()
    
    
    #{:%Y-%m-%d %H:%M}