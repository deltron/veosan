'''
Created on Mar 17, 2012

@author: phil
'''

#from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import logging
from datetime import datetime, timedelta
from webapp2_extras.appengine.auth.models import User

'''
    stored data 
'''

class Patient(ndb.Model):
    '''
    A patient
    '''
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    #user = db.UserProperty()
    user = ndb.KeyProperty(kind=User)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    telephone = ndb.StringProperty()
    terms_agreement = ndb.BooleanProperty()
    # insurance
    # age

class Provider(ndb.Model):
    '''
    A provider
    '''
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    activation_key = ndb.StringProperty()
    
    # terms
    terms_agreement = ndb.BooleanProperty()
    terms_date = ndb.DateProperty()
    
    # profile
    category = ndb.StringProperty()
    specialty = ndb.StringProperty(repeated=True)
    associations = ndb.StringProperty(repeated=True)
    certifications = ndb.StringProperty(repeated=True)
    onsite = ndb.BooleanProperty()
    start_year = ndb.StringProperty()
    
    # address
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    prefix = ndb.StringProperty()
    postfix = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    location = ndb.StringProperty()
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    postal_code = ndb.StringProperty()
    profile_photo_blob = ndb.BlobKeyProperty()
    bio = ndb.TextProperty()
    quote = ndb.TextProperty()
    # schedule
    # see Schedule Class below

    
    def fullName(self):
        return '{0} {1}, {2}'.format(self.first_name, self.last_name, self.category)
    
    def get_edit_link(self, section='address'):
        return u'/provider/%s?key=%s' % (section, self.key.urlsafe())
    
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
        
class Schedule(ndb.Model):
    provider = ndb.KeyProperty(kind=Provider) # name='schedule'
    day = ndb.IntegerProperty()
    startTime = ndb.IntegerProperty()
    endTime = ndb.IntegerProperty()
    
    def repr(self):
        # String representation for debuging, I'm too scared to override the __repr__() 
        return '[Schedule day:%s from %s to %s]' % (self.day, self.startTime, self.endTime)
    
class Booking(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    #request
    requestCategory = ndb.StringProperty()
    requestRegion = ndb.StringProperty()
    requestDateTime = ndb.DateTimeProperty()
    # email for booking requests with no provider found
    request_email = ndb.StringProperty()
    # actual appointment
    dateTime = ndb.DateTimeProperty()
    comments = ndb.TextProperty()
    # link to patient
    patient = ndb.KeyProperty(kind=Patient)
    # link to provider
    provider = ndb.KeyProperty(kind=Provider)
    
    def get_html_summary(self):
        s = u''
        fields_dict = vars(self).iteritems()
        for k, v in fields_dict:
            if (k != '_entity'):
                s += u'%s: %s <br>' % (k[1:], v)
        return s

