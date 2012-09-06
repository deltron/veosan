from google.appengine.ext import ndb
import logging
from webapp2_extras.appengine.auth.models import User as Webapp2AuthUser
import util
from datetime import datetime, timedelta, date, time

'''
    stored data 
'''

class SiteConfig(ndb.Model):
    booking_enabled = ndb.BooleanProperty(default=False)
    google_analytics_enabled = ndb.BooleanProperty(default=False)
    facebook_like_enabled = ndb.BooleanProperty(default=False)
    signup_enabled = ndb.BooleanProperty(default=False)
    error_email_enabled = ndb.BooleanProperty(default=False)


class SiteLog(ndb.Model):
    page = ndb.StringProperty()
    access_time = ndb.DateTimeProperty(auto_now_add=True)
    ip = ndb.StringProperty()
    referer = ndb.TextProperty()
    language = ndb.StringProperty()
    user = ndb.KeyProperty(kind='User')
    user_email = ndb.StringProperty()
    admin_email = ndb.StringProperty()

    gae_country = ndb.StringProperty()
    gae_region = ndb.StringProperty()
    gae_city = ndb.StringProperty()
    gae_city_lat_long = ndb.StringProperty()


class SiteCounter(ndb.Model):
    internet_explorer_hits = ndb.IntegerProperty(default=0)
    log_email_last_offset = ndb.StringProperty()
    blog_clicks = ndb.IntegerProperty(default=0)
    blog_clicks_en = ndb.IntegerProperty(default=0)
    blog_clicks_fr = ndb.IntegerProperty(default=0)


class PartialProvider(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    gae_country = ndb.StringProperty()
    gae_region = ndb.StringProperty()
    gae_city = ndb.StringProperty()
    gae_city_lat_long = ndb.StringProperty()

class User(Webapp2AuthUser):
    '''
        Extending the Webapp2 Auth User to add roles
    '''
    roles = ndb.StringProperty(repeated=True)
    
    signup_token = ndb.StringProperty()
    resetpassword_token = ndb.StringProperty()
       
    confirmed = ndb.BooleanProperty()

    language = ndb.StringProperty(default='en')

    def get_email(self):
        return self.auth_ids[0]
    
    def is_activated_and_has_password(self):
        return (self.password != None) & (self.signup_token == None)


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
    
    # address from AppEngine
    gae_country = ndb.StringProperty()
    gae_region = ndb.StringProperty()
    gae_city = ndb.StringProperty()
    gae_city_lat_long = ndb.StringProperty()

    
    # Address for homecare
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    postal_code = ndb.StringProperty()
    province = ndb.StringProperty()
    
    def get_bookings(self):
        return Booking.query(Booking.patient == self.key).fetch()
    
    def get_future_bookings(self):
        return Booking.query(Booking.patient == self.key, Booking.datetime >= datetime.now()).fetch()
    
    def get_future_unconfirmed_bookings(self):
        return Booking.query(Booking.patient == self.key, Booking.datetime >= datetime.now(), Booking.confirmed==False).fetch()



class LogEvent(ndb.Model):
    user = ndb.KeyProperty(kind=User)
    admin = ndb.BooleanProperty(default=False)

    created_on = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.StringProperty()
    referer = ndb.StringProperty()


class Schedule(ndb.Model):
    provider = ndb.KeyProperty(kind='Provider') # name='schedule'
    day = ndb.StringProperty()
    start_time = ndb.IntegerProperty()
    end_time = ndb.IntegerProperty()
    
    def _pre_put_hook(self):
        ''' Checks if about-to-be-saved schedule overlaps an existing schedule. if yes, merges them and deletes the old schedule'''
        #logging.info('Schedule overlap check (pre-put)')
        sq = Schedule.query(Schedule.provider == self.provider, Schedule.day == self.day)
        for s in sq:
            if self.overlaps(s):
                logging.info('Schedules overlap, merging %s %s' % (self, s))
                self.merge(s)
                logging.info('Merged schedule into %s' % self)
                logging.info('deleting merged schedule %s' % s)
                s.key.delete()
        
    def __repr__(self):
        return '[%s from %s-%s]' % (self.day, self.start_time, self.end_time)

    def overlaps(self, s):
        ''' Returns true if schedule s overlaps or touches (start == end) the current schedule '''
        # same day
        if self.day != s.day:
            return False
        if self.start_time < s.start_time:
            early = self
            late = s
        elif self.start_time > s.start_time:
            early = s
            late = self
        else:
            # same start_time is an overlap
            return True
        return early.end_time >= late.start_time

    def merge(self, s):
        ''' merged sechdule s into the current schedule '''
        if s.day == self.day:
            self.start_time = min(self.start_time, s.start_time)
            self.end_time = max(self.end_time, s.end_time)

    @property
    def span(self):
        return self.end_time - self.start_time
    
    
 
class Note(ndb.Model):
    provider = ndb.KeyProperty(kind='Provider')
    body = ndb.TextProperty()
    note_type = ndb.StringProperty(choices=util.note_types) 
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty()
    event_date = ndb.DateProperty(auto_now_add=True)
    
    def get_icon_name(self):
        if self.note_type == 'call':
            return 'icon-comment'
        elif self.note_type == 'meeting':
            return 'icon-plane'
        elif self.note_type == 'admin':
            return 'icon-wrench'
        else:
            return 'icon-question-sign'
    
    
class Booking(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    # differentialte public profile bookings from search bookings
    booking_source = ndb.StringProperty(choices=['search', 'profile'])
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
    specialty = ndb.StringProperty()
    insurance = ndb.StringProperty()
    
    
    
    # link to patient
    patient = ndb.KeyProperty(kind='Patient')
    
    # link to provider
    provider = ndb.KeyProperty(kind='Provider')
    
    # link to schedule object this booking is "inside"
    schedule = ndb.KeyProperty(kind='Schedule')
    
    # booking confirmed by patient
    confirmed = ndb.BooleanProperty(default=False)
    
    status = ndb.StringProperty()

    def get_html_summary(self):
        s = u''
        fields_dict = vars(self).iteritems()
        for k, v in fields_dict:
            if (k != '_entity'):
                s += u'%s: %s <br>' % (k[1:], v)
        return s
    
    
