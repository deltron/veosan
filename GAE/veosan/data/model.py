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
    
    def get_future_bookings(self):
        return Booking.query(Booking.patient == self.key, Booking.datetime >= datetime.now()).fetch()
    


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
    display_welcome_page = ndb.BooleanProperty(default=True)
    connect_enabled = ndb.BooleanProperty(default=False)

    # user
    user = ndb.KeyProperty(kind=User)

    
    def get_profile_photo_image_url(self, size=None):
        return get_serving_url(self.profile_photo_blob_key, size)

    def obfuscated_name(self):
        if self.last_name:
            first_letter_of_last_name = self.last_name[0]
        return "%s %s %s." % (self.title, self.first_name, first_letter_of_last_name)
        
    def full_name(self):
        return '%s %s %s' % (self.title, self.first_name, self.last_name)
    

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
    
    def get_total_available_hours_per_week(self):
        sq = self.get_schedules()
        return reduce(lambda sum, s: sum + (s.end_time - s.start_time), sq, 0)
    
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

    def is_enabled(self):
        return self.status == 'client_enabled'
    
    def get_provider_network_count(self):     
        sources = ProviderNetworkConnection.query(ProviderNetworkConnection.source_provider == self.key, ProviderNetworkConnection.confirmed == True).count()
        targets = ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == True).count()
        
        return sources + targets
        
    def get_provider_network(self):     
        sources = ProviderNetworkConnection.query(ProviderNetworkConnection.source_provider == self.key, ProviderNetworkConnection.confirmed == True).fetch()
        targets = ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == True).fetch()
        
        provider_keys = []
        
        for connect in sources:
            provider_keys.append(connect.target_provider)
            
        for connect in targets:
            provider_keys.append(connect.source_provider)

        providers = ndb.get_multi(provider_keys)

        return providers
    
    def is_connected_to(self, provider):
        if provider.key == self.key:
            return False
        else:
            return provider in self.get_provider_network()
    
    def get_provider_network_pending_count(self):     
        targets = ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == False).count()
        
        return targets
    
    
    def get_provider_network_pending(self):     
        targets = ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == False).fetch()
        
        providers = []
        for connect in targets:
            providers.append(connect.source_provider.get())

        return providers

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

class Invite(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)

    provider = ndb.KeyProperty(kind=Provider)
    token = ndb.StringProperty()
    link_clicked = ndb.BooleanProperty(default=False)
    profile_created = ndb.BooleanProperty(default=False)

    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    note = ndb.TextProperty()


class ProviderNetworkConnection(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    
    invite = ndb.KeyProperty(kind=Invite)

    source_provider = ndb.KeyProperty(kind=Provider)
    target_provider = ndb.KeyProperty(kind=Provider)
    relationship = ndb.StringProperty()
    confirmed = ndb.BooleanProperty(default=False)

    
    def _pre_put_hook(self):
        # don't connect with yourself
        if self.source_provider == self.target_provider:
            raise Exception('Invalid connection to self')
                
        # remove any dupes from the network graph
        
        # check for duplicate source->target
        source_target_count = ProviderNetworkConnection.query(
                            ProviderNetworkConnection.source_provider == self.source_provider,
                            ProviderNetworkConnection.target_provider == self.target_provider,
                            ProviderNetworkConnection.confirmed == True,
                            ).count()
        
        if source_target_count > 0:
            raise Exception('Duplicate source to target')

        # check for duplicate target->source
        source_target_count = ProviderNetworkConnection.query(
                            ProviderNetworkConnection.target_provider == self.source_provider,
                            ProviderNetworkConnection.source_provider == self.target_provider, 
                            ProviderNetworkConnection.confirmed == True,
                            ).count()
        
        if source_target_count > 0:
            raise Exception('Duplicate target to source')


class PatientNetworkConnection(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)

    source_provider = ndb.KeyProperty(kind=Provider)
    target_patient = ndb.KeyProperty(kind=Patient)
    relationship = ndb.StringProperty()
    status = ndb.StringProperty()


class Schedule(ndb.Model):
    provider = ndb.KeyProperty(kind=Provider) # name='schedule'
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
    provider = ndb.KeyProperty(kind=Provider)
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
    
    
