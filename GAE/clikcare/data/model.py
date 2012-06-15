from google.appengine.ext import ndb
import logging
from datetime import datetime, timedelta
from webapp2_extras.appengine.auth.models import User as Webapp2AuthUser

'''
    stored data 
'''

# headers must be strings not unicode
def get_link(model_entity, route=None):
    if route:
        return '%s?key=%s' % (route, model_entity.key.urlsafe())
    else:
        logging.error('(model.get_link) Trying to get route key with no route')
    

class User(Webapp2AuthUser):
    '''
        Extending the Webapp2 Auth User to add roles
    '''
    roles = ndb.StringProperty(repeated=True)
    
    # for now...
    # replace with dictionnary later...
    # better yet find a way to mash into the webapp2 user token model
    signup_token = ndb.StringProperty()
    resetpassword_token = ndb.StringProperty()
    
    
    confirmed = ndb.BooleanProperty()
    
    def get_email(self):
        return self.auth_ids[0]


class Patient(ndb.Model):
    '''
    A patient
    '''
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.KeyProperty(kind=User)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    telephone = ndb.StringProperty()
    terms_agreement = ndb.BooleanProperty()

    # insurance
    # age    

    def get_bookings(self):
        return Booking.query(Booking.patient == self.key).fetch()
    


class Provider(ndb.Model):
    '''
    A provider
    '''
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    enable = ndb.BooleanProperty()

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
    title = ndb.StringProperty()
    credentials = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    location = ndb.StringProperty()
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    postal_code = ndb.StringProperty()
    profile_photo_blob_key = ndb.BlobKeyProperty()
    bio = ndb.TextProperty()
    quote = ndb.TextProperty()
    
    # user
    user = ndb.KeyProperty(kind=User)
    
    def get_edit_link(self, route='/provider/bookings'):
        return get_link(self, route)
 
    def fullName(self):
        return '{0} {1}'.format(self.first_name, self.last_name)
    

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
    
    def get_schedule(self):
        return Schedule.query(Schedule.provider == self.key)
    
    def getAvailableScheduleIds(self):
        logging.info('Getting schedules for provider: %s' % self.key);
        ids = list()
        sq = Schedule.query(Schedule.provider == self.key)
        logging.info('schedule count %s' % sq.count())
        for s in sq:
            schedule_id = str(s.day) + '-' + str(s.startTime) + '-' + str(s.endTime)
            ids.append(schedule_id)
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
    request_category = ndb.StringProperty()
    request_location = ndb.StringProperty()
    request_datetime = ndb.DateTimeProperty()
    request_email = ndb.StringProperty()
    
    # actual appointment
    request_datetime = ndb.DateTimeProperty()
    comments = ndb.TextProperty()
    # link to patient
    patient = ndb.KeyProperty(kind=Patient)
    # link to provider
    provider = ndb.KeyProperty(kind=Provider)
    
    confirmed = ndb.BooleanProperty()
    
    def get_html_summary(self):
        s = u''
        fields_dict = vars(self).iteritems()
        for k, v in fields_dict:
            if (k != '_entity'):
                s += u'%s: %s <br>' % (k[1:], v)
        return s
    
    
