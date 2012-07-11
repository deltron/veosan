from google.appengine.ext import ndb
import logging
from datetime import datetime, timedelta, date, time
from webapp2_extras.appengine.auth.models import User as Webapp2AuthUser
from google.appengine.api import users
from google.appengine.api.images import get_serving_url
import util

'''
    stored data 
'''

class SiteConfig(ndb.Model):
    booking_enabled = ndb.BooleanProperty()
    

class User(Webapp2AuthUser):
    '''
        Extending the Webapp2 Auth User to add roles
    '''
    roles = ndb.StringProperty(repeated=True)
    
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
    # Address for homecare
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    postal_code = ndb.StringProperty()

    # insurance
    # age    

    def get_bookings(self):
        return Booking.query(Booking.patient == self.key).fetch()
    


class Provider(ndb.Model):
    '''
    A provider
    '''
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    # sales status
    status = ndb.StringProperty(default='prospect', choices=util.provider_statuses)

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
    
    # unique name for public profile
    # possible coercion to lower case?
    vanity_url = ndb.StringProperty()
    
    # account options
    booking_enabled = ndb.BooleanProperty(default=False)
    address_enabled = ndb.BooleanProperty(default=False)
    
    # user
    user = ndb.KeyProperty(kind=User)
    
    def get_profile_photo_image_url(self, size=None):
        return get_serving_url(self.profile_photo_blob_key, size)

    def obfuscated_name(self):
        if self.last_name:
            first_letter_of_last_name = self.last_name[0]
        return "%s %s %s." % (self.title, self.first_name, first_letter_of_last_name)
        
    def full_name(self):
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
    
    def get_future_bookings(self):
        yesterday_at_midnight = datetime.combine(date.today(), time())
        future_bookings = Booking.query(Booking.provider == self.key).order(Booking.datetime).fetch(50)
        #, Booking.request_datetime > yesterday_at_midnight
        return future_bookings
    
    def get_notes(self):
        ''' Get Notes in reverse chronological order'''
        return Note.query(Note.provider == self.key).order(-Note.created_on)
    
    def get_education(self):
        return Education.query(Education.provider == self.key).order(-Education.end_year)

    def get_experience(self):
        return Experience.query(Experience.provider == self.key).order(-Experience.end_year)

    def add_note(self, body, note_type='admin'):
        ''' Add Note to this provider'''
        note = Note()
        note.provider = self.key
        note.body = body
        logging.info('note_type %s' % note_type)
        note.note_type = note_type
        note.user = users.get_current_user()
        note.put()
        
    def is_enabled(self):
        return self.status == 'client_enabled'
    

class Education(ndb.Model):  
    provider = ndb.KeyProperty(kind=Provider)
 
    start_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()

    school_name = ndb.StringProperty()
    degree_type = ndb.StringProperty()
    degree_text = ndb.StringProperty()

    description = ndb.StringProperty()

class Experience(ndb.Model):   
    provider = ndb.KeyProperty(kind=Provider)

    start_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()

    company_name = ndb.StringProperty()
    title = ndb.StringProperty()

    description = ndb.TextProperty()




class Schedule(ndb.Model):
    provider = ndb.KeyProperty(kind=Provider) # name='schedule'
    day = ndb.IntegerProperty()
    startTime = ndb.IntegerProperty()
    endTime = ndb.IntegerProperty()
    
    def repr(self):
        # String representation for debuging, I'm too scared to override the __repr__() 
        return '[Schedule day:%s from %s to %s]' % (self.day, self.startTime, self.endTime)
 
 
class Note(ndb.Model):
    provider = ndb.KeyProperty(kind=Provider)
    body = ndb.TextProperty()
    note_type = ndb.StringProperty(choices=util.note_types) 
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty()
    #datetime = ndb.DateTimeProperty(auto_now_add=True)
    
    def get_icon_name(self):
        if self.note_type  == 'call':
            return 'icon-comment'
        elif self.note_type =='meeting':
            return 'icon-plane'
        elif self.note_type == 'admin':
            return 'icon-wrench'
        else:
            return 'icon-question-sign'
    
    
class Booking(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    #request
    request_category = ndb.StringProperty()
    request_location = ndb.StringProperty()
    request_homecare = ndb.BooleanProperty()
    request_datetime = ndb.DateTimeProperty()
    request_email = ndb.StringProperty()
    
    search_results = ndb.KeyProperty(repeated=True)
    
    # actual appointment
    datetime = ndb.DateTimeProperty()
    comments = ndb.TextProperty()
    # link to patient
    patient = ndb.KeyProperty(kind=Patient)
    # link to provider
    provider = ndb.KeyProperty(kind=Provider)
    
    confirmed = ndb.BooleanProperty()
    
    status = ndb.StringProperty()
    
    def get_html_summary(self):
        s = u''
        fields_dict = vars(self).iteritems()
        for k, v in fields_dict:
            if (k != '_entity'):
                s += u'%s: %s <br>' % (k[1:], v)
        return s
    
    
