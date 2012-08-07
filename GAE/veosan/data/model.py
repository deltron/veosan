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
    booking_enabled = ndb.BooleanProperty(default=False)
    google_analytics_enabled = ndb.BooleanProperty(default=False)
    facebook_like_enabled = ndb.BooleanProperty(default=False)
    signup_enabled = ndb.BooleanProperty(default=False)


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
    practice_sites = ndb.StringProperty(repeated=True)
    spoken_languages = ndb.StringProperty(repeated=True)
    profile_photo_blob_key = ndb.BlobKeyProperty()
    bio = ndb.TextProperty()
    quote = ndb.TextProperty()

    # address
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    title = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    postal_code = ndb.StringProperty()
    province = ndb.StringProperty()
    
    # deprecated
    associations = ndb.StringProperty(repeated=True)
    certifications = ndb.StringProperty(repeated=True)
    start_year = ndb.StringProperty()
    location = ndb.StringProperty()
    credentials = ndb.StringProperty()
    
    # unique name for public profile
    # possible coercion to lower case?
    vanity_url = ndb.StringProperty()
    vanity_domain = ndb.StringProperty()
    profile_views = ndb.IntegerProperty(default=0)
    
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
    
    def get_schedules(self):
        return Schedule.query(Schedule.provider == self.key).order(Schedule.day, Schedule.start_time)
    
    def isAvailable(self, day, time):
        count = self.schedule.filter('day = ', day).filter('time = ', time).count()
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
    
    def order_cv_results(self, all):
        # has a last_year attribute
        completed = filter(lambda e: e.end_year != None, all)
        
        # present means no last_year attribute
        present = filter(lambda e: e.end_year == None, all)
        
        # show present before completed
        present.extend(completed)
        
        return present

    def get_education(self):
        return self.order_cv_results(Education.query(Education.provider == self.key).order(-Education.end_year, -Education.start_year))

    def get_experience(self):
        return self.order_cv_results(Experience.query(Experience.provider == self.key).order(-Experience.end_year, -Experience.start_year))

    def get_continuing_education(self):
        return ContinuingEducation.query(ContinuingEducation.provider == self.key).order(-ContinuingEducation.year, -ContinuingEducation.month)

    def get_organization(self):
        return ProfessionalOrganization.query(ProfessionalOrganization.provider == self.key).order(-ProfessionalOrganization.end_year, -ProfessionalOrganization.start_year)

    def get_certification(self):
        return ProfessionalCertification.query(ProfessionalCertification.provider == self.key).order(-ProfessionalCertification.year)

    def get_cv_items_count(self):
        return sum([
                   Education.query(Education.provider == self.key).count(),
                   Experience.query(Experience.provider == self.key).count(),
                   ContinuingEducation.query(ContinuingEducation.provider == self.key).count(),
                   ProfessionalOrganization.query(ProfessionalOrganization.provider == self.key).count(),
                   ProfessionalCertification.query(ProfessionalCertification.provider == self.key).count(),
                ])

    def is_address_complete(self):
        if (not self.phone or (self.phone and len(self.phone) < 10)):
            return False
        if (not self.address or (self.address and len(self.address) < 3)):
            return False
        if (not self.city or (self.city and len(self.city) < 3)):
            return False
        if (not self.postal_code or (self.postal_code and len(self.postal_code) < 6)):
            return False
        if (not self.province or (self.province and len(self.province) < 2)):
            return False
        if (not self.first_name or (self.first_name and len(self.first_name) < 2)):
            return False
        if (not self.last_name or (self.last_name and len(self.last_name) < 2)):
            return False
        return True

        
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
    other = ndb.StringProperty()
    location = ndb.StringProperty()

    degree_type = ndb.StringProperty()
    degree_title = ndb.StringProperty()

    description = ndb.TextProperty()


class ContinuingEducation(ndb.Model):  
    provider = ndb.KeyProperty(kind=Provider)
 
    year = ndb.IntegerProperty()
    month = ndb.IntegerProperty()

    hours = ndb.FloatProperty()

    type = ndb.StringProperty()

    title = ndb.StringProperty()

    description = ndb.StringProperty()


class Experience(ndb.Model):   
    provider = ndb.KeyProperty(kind=Provider)

    start_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()

    company_name = ndb.StringProperty()
    title = ndb.StringProperty()
    location = ndb.StringProperty()

    description = ndb.TextProperty()


class ProfessionalOrganization(ndb.Model):   
    provider = ndb.KeyProperty(kind=Provider)
    organization = ndb.StringProperty()
    other = ndb.StringProperty()
    start_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()
    location = ndb.StringProperty()
    
class ProfessionalCertification(ndb.Model):   
    provider = ndb.KeyProperty(kind=Provider)
    certification = ndb.StringProperty()
    other = ndb.StringProperty()
    year = ndb.IntegerProperty()


class LogEvent(ndb.Model):
    user = ndb.KeyProperty(kind=User)
    admin = ndb.BooleanProperty(default=False)

    created_on = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.StringProperty()
    referer = ndb.StringProperty()


class Schedule(ndb.Model):
    provider = ndb.KeyProperty(kind=Provider) # name='schedule'
    day = ndb.StringProperty()
    start_time = ndb.IntegerProperty()
    end_time = ndb.IntegerProperty()
    
    def __repr__(self):
        return 'Schedule %s %s-%s' % (self.day, self.start_time, self.end_time)

    @property
    def span(self):
        return self.end_time - self.start_time
    
    
 
class Note(ndb.Model):
    provider = ndb.KeyProperty(kind=Provider)
    body = ndb.TextProperty()
    note_type = ndb.StringProperty(choices=util.note_types) 
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty()
    #datetime = ndb.DateTimeProperty(auto_now_add=True)
    
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
    
    
