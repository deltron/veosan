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
    created_on = db.DateTimeProperty(auto_now_add=True)
    user = db.UserProperty()
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    email = db.StringProperty()
    telephone = db.StringProperty()
    terms_agreement = db.BooleanProperty()
    # insurance
    # age

class Provider(db.Model):
    '''
    A provider
    '''
    created_on = db.DateTimeProperty(auto_now_add=True)
    activation_key = db.StringProperty()
    
    # terms
    terms_agreement = db.BooleanProperty()
    terms_date = db.DateProperty()
    
    # profile
    category = db.StringProperty()
    specialty = db.StringListProperty()
    associations = db.StringListProperty()
    certifications = db.StringListProperty()
    onsite = db.BooleanProperty()
    start_year = db.StringProperty()
    
    # address
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    prefix = db.StringProperty()
    postfix = db.StringProperty()
    email = db.StringProperty()
    phone = db.StringProperty()
    region = db.StringProperty()
    address = db.StringProperty()
    city = db.StringProperty()
    postal_code = db.StringProperty()
    profile_photo_blob = blobstore.BlobReferenceProperty()
    bio = db.StringProperty(multiline=True)
    quote = db.StringProperty(multiline=True)
    
    
    # schedule
    # see Schedule Class below
    
    def fullName(self):
        return '{0} {1}, {2}'.format(self.first_name, self.last_name, self.category)
    
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
        return self.created_on > datetime_24h_ago
    
    def getAvailableScheduleIds(self):
        ids = list()
        for s in self.schedule:
            id = str(s.day) + '-' + str(s.startTime) + '-' + str(s.endTime)
            ids.append(id)
        return ids
    
    def isAvailable(self, day, time):
        count =  self.schedule.filter('day = ', day).filter('time = ', time).count()
        logging.info("is available? " + str(day) + " " + str(time) + " count:" + str(count))
        return count > 0
        
class Schedule(db.Model):
    provider = db.ReferenceProperty(Provider, collection_name='schedule')
    day = db.IntegerProperty()
    startTime = db.IntegerProperty()
    endTime = db.IntegerProperty()
    
    def repr(self):
        # String representation for debuging, I'm too scared to override the __repr__() 
        return '[Schedule day:%s from %s to %s]' % (self.day, self.startTime, self.endTime)
    
class Booking(db.Model):
    created_on = db.DateTimeProperty(auto_now_add=True)
    #request
    requestCategory = db.StringProperty()
    requestRegion = db.StringProperty()
    requestDateTime = db.DateTimeProperty()
    # email for booking requests with no provider found
    requestEmail = db.EmailProperty()
    # actual appointment
    dateTime = db.DateTimeProperty()
    comments = db.StringProperty(multiline=True)
    # link to patient
    patient = db.ReferenceProperty(Patient)
    # link to provider
    provider = db.ReferenceProperty(Provider)
    
    def get_html_summary(self):
        s = u''
        fields_dict = vars(self).iteritems()
        for k, v in fields_dict:
            if (k != '_entity'):
                s += u'%s: %s <br>' % (k[1:], v)
        return s

