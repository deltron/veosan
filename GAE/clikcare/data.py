'''
Created on Mar 17, 2012

@author: phil
'''

from google.appengine.ext import db
from google.appengine.ext import blobstore
import logging
from datetime import datetime, timedelta

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
    # schedule
    # see Schedule Class below
    
    def get_edit_link(self, section='address'):
        return u'/provider/%s?key=%s' % (section, self.key())
    
    def get_html_summary(self):
        s = u''
        fields_dict = vars(self).iteritems()
        for k, v in fields_dict:
            if (k != '_entity'):
                s += u'%s: %s <br>' % (k[1:], v)
        return s
    
    def recently_created(self):
        datetime_24h_ago = datetime.now() - timedelta(hours=24)
        return self.createdOn > datetime_24h_ago
    
    def getAvailableScheduleIds(self):
        ids = list()
        for s in self.schedule:
            id = str(s.day) + '-' + str(s.time)
            ids.append(id)
        return ids
    
    def isAvailable(self, day, time):
        count =  self.schedule.filter('day = ', day).filter('time = ', time).count()
        logging.info("is available? " + str(day) + " " + str(time) + " count:" + str(count))
        return count > 0
        
class Schedule(db.Model):
    provider = db.ReferenceProperty(Provider, collection_name='schedule')
    day = db.IntegerProperty()
    time = db.IntegerProperty()
    
    
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
    # link to provider
    provider = db.ReferenceProperty(Provider)    

