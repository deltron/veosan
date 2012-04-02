'''
Created on Mar 17, 2012

@author: phil
'''

from google.appengine.ext import db
from google.appengine.ext import blobstore
import logging

'''
    stored data 
'''

class Patient(db.Model):
    '''
    A patient
    '''
    createdOn = db.DateTimeProperty(auto_now_add=True)
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    email = db.StringProperty()
    phone = db.StringProperty()


class Provider(db.Model):
    '''
    A provider
    '''
    createdOn = db.DateTimeProperty(auto_now_add=True)
    # profile
    category = db.StringProperty()
    specialty = db.StringProperty()
    school = db.StringProperty()
    degree = db.StringProperty()
    startYear = db.StringProperty()
    # address
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    email = db.StringProperty()
    phone = db.StringProperty()   
    region = db.StringProperty()
    address = db.StringProperty()
    city = db.StringProperty()
    postalCode = db.StringProperty()
    profilePhotoBlobKey = blobstore.BlobReferenceProperty()
    
    def get_edit_link(self, section='address'):
        return u'/provider/%s?key=%s' % (section, self.key())
    
    def get_html_summary(self):
        s = u''
        fields_dict = vars(self).iteritems()
        for k, v in fields_dict:
            if (k != '_entity'):
                s += u'%s: %s <br>' % (k, v)
        return s

    
class Booking(db.Model):
    '''
    A booking
    '''
    createdOn = db.DateTimeProperty(auto_now_add=True)
    #author = db.UserProperty()
    requestSpecialty = db.StringProperty()
    requestLocation = db.StringProperty()
    requestDate = db.StringProperty()
    requestTime = db.StringProperty()
    requestContact = db.StringProperty()
    telephoneConfirmation = db.BooleanProperty(default=False)
    comments = db.StringProperty(multiline=True)
    # link to patient
    patient = db.ReferenceProperty(Patient)
        

