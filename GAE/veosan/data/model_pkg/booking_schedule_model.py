from google.appengine.ext import ndb
import logging

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
                logging.debug('Schedules overlap, merging %s %s' % (self, s))
                self.merge(s)
                logging.debug('Merged schedule into %s' % self)
                logging.debug('deleting merged schedule %s' % s)
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
    
    
 
    
class Booking(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    # differentialte public profile bookings from search bookings
    booking_source = ndb.StringProperty(choices=['search', 'profile'])
    
    # actual appointment
    datetime = ndb.DateTimeProperty()
    comments = ndb.TextProperty()
    
    #### deprecated...for now!
    specialty = ndb.StringProperty()
    insurance = ndb.StringProperty()
    ####
    
    #request
    # maybe deprecated?
    request_category = ndb.StringProperty()
    request_location = ndb.StringProperty()
    request_homecare = ndb.BooleanProperty()
    request_datetime = ndb.DateTimeProperty()
    request_email = ndb.StringProperty()
    search_results = ndb.KeyProperty(repeated=True)
    status = ndb.StringProperty()
    ####

    
    # link to patient
    patient = ndb.KeyProperty(kind='Patient')
    
    # link to provider
    provider = ndb.KeyProperty(kind='Provider')
    
    # link to schedule object this booking is "inside"
    schedule = ndb.KeyProperty(kind='Schedule')
    
    # booking confirmed by patient
    confirmed = ndb.BooleanProperty(default=False)
    email_sent_to_patient = ndb.BooleanProperty(default=False)
    