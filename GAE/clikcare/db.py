'''
Created on Mar 17, 2012

@author: phil
'''

from google.appengine.ext import db



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
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    email = db.StringProperty()
    phone = db.StringProperty()    
    specialty = db.StringProperty()
    
    
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
        
        