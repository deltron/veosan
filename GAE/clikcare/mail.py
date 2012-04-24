
import logging
from google.appengine.api import mail

CLIK_SUPPORT_ADDRESS = 'philippe.caya@gmail.com'

def emailBooking(booking):
    ''' send booking info to patient, provider and us '''
    patient = booking.patient
    to_address = patient.email
    # check email valid
    if not mail.is_email_valid(to_address):
        logging.warn('Email is not valid: {0}. Trying anyway...' %  to_address)
    # create message
    message = mail.EmailMessage()
    message.sender = CLIK_SUPPORT_ADDRESS
    message.to = to_address
    message.body = """
Your are booked!

%s
    """ % booking.__dict__
    # send message
    message.send()