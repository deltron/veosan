from google.appengine.ext import ndb
from datetime import datetime, timedelta, date, time
from google.appengine.api.images import get_serving_url
from data.model_pkg.cv_model import Education, Experience, ContinuingEducation,\
    ProfessionalOrganization, ProfessionalCertification, Specialty
from data.model_pkg.network_model import ProviderNetworkConnection
import utilities
from webapp2_extras.i18n import to_utc
from data.model_pkg.site_model import SiteLog
from data.model_pkg.booking_schedule_model import Schedule, Booking,\
    ProviderService

class ProviderAccount(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    provider = ndb.KeyProperty(kind='Provider')
    stripe_customer_id = ndb.StringProperty()
    stripe_plan_id = ndb.StringProperty()
    

class Provider(ndb.Model):
    '''
    A provider
    '''
    created_on = ndb.DateTimeProperty(auto_now_add=True)

    # signup origin
    signup_origin = ndb.StringProperty()

    # terms
    terms_agreement = ndb.BooleanProperty()
    terms_date = ndb.DateProperty()
        
    # profile
    category = ndb.StringProperty()
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
    
    # address from AppEngine
    gae_country = ndb.StringProperty()
    gae_region = ndb.StringProperty()
    gae_city = ndb.StringProperty()
    gae_city_lat_long = ndb.StringProperty()

    
    # possible coercion to lower case?
    vanity_url = ndb.StringProperty()
    vanity_domain = ndb.StringProperty()
    domain = ndb.StringProperty()
    profile_views = ndb.IntegerProperty(default=0)
    profile_language = ndb.StringProperty()

    
    # account options
    booking_enabled = ndb.BooleanProperty(default=False)
    address_enabled = ndb.BooleanProperty(default=True)
    display_welcome_page = ndb.BooleanProperty(default=True)
    connect_enabled = ndb.BooleanProperty(default=True)
    stats_enabled = ndb.BooleanProperty(default=False)
    upgrade_enabled = ndb.BooleanProperty(default=True)


    # user
    user = ndb.KeyProperty(kind='User')

    # deprecated ---------------
    associations = ndb.StringProperty(repeated=True)
    certifications = ndb.StringProperty(repeated=True)
    start_year = ndb.StringProperty()
    location = ndb.StringProperty()
    credentials = ndb.StringProperty()
    # end deprecated
    
    def get_profile_photo_image_url(self, size=None, secure_url=True):
        return get_serving_url(self.profile_photo_blob_key, size=size, secure_url=secure_url)

    def recently_created(self):
        datetime_24h_ago = datetime.now() - timedelta(hours=24)
        return self.created_on > datetime_24h_ago
    
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
    
    ###################################################################
    # Schedules and bookings
    #    
    def get_schedules(self):
        return Schedule.query(Schedule.provider == self.key).order(Schedule.day, Schedule.start_time)
    
    def get_total_available_hours_per_week(self):
        sq = self.get_schedules()
        return reduce(lambda sum, s: sum + (s.end_time - s.start_time), sq, 0)
    
    def is_available(self, book_date, book_time):
        return self.is_booking_inside_schedule(book_date, book_time) and self.is_timeslot_free(book_date, book_time)
    
    def is_booking_inside_schedule(self, book_date, book_time):
        schedules = self.get_schedules()
        for schedule in schedules:
            if self.is_book_date_and_time_inside_schedule(schedule, book_date, book_time):
                return True
        
    def is_timeslot_free(self, book_date, book_time):
        booking_datetime = to_utc(datetime.strptime(book_date + " " + book_time, '%Y-%m-%d %H'))
        
        for booking in self.get_future_confirmed_bookings():
            if booking.datetime == booking_datetime:
                return False
                
        return True
        
    def is_book_date_and_time_inside_schedule(self, schedule, book_date, book_time):
        book_weekday_index = datetime.strptime(book_date, '%Y-%m-%d').weekday()
        (book_weekday_key, book_weekday_label) = utilities.time.get_day_of_the_week_from_python_weekday(book_weekday_index)
        book_time_int = int(book_time)

        if book_weekday_key == schedule.day:
            if book_time_int >= schedule.start_time and book_time_int <= schedule.end_time:
                return True
    
    def get_future_confirmed_bookings(self):
        yesterday_at_midnight = datetime.combine(date.today(), time())
        future_confirmed_bookings = Booking.query(Booking.provider == self.key, Booking.datetime >= yesterday_at_midnight, Booking.confirmed==True).order(Booking.datetime).fetch()
        return future_confirmed_bookings
    
    def get_all_future_bookings(self):
        yesterday_at_midnight = datetime.combine(date.today(), time())
        all_future_bookings = Booking.query(Booking.provider == self.key, Booking.datetime >= yesterday_at_midnight).order(Booking.datetime).fetch()
        return all_future_bookings

    def get_provider_services(self):
        return ProviderService.query(ProviderService.provider == self.key)
    
    ###################################################################
    # CV
    #    
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

    def get_specialty(self):
        return Specialty.query(Specialty.provider == self.key)

    def get_cv_items_count(self):
        return sum([
                   Education.query(Education.provider == self.key).count(),
                   Experience.query(Experience.provider == self.key).count(),
                   ContinuingEducation.query(ContinuingEducation.provider == self.key).count(),
                   ProfessionalOrganization.query(ProfessionalOrganization.provider == self.key).count(),
                   ProfessionalCertification.query(ProfessionalCertification.provider == self.key).count(),
                ])


    
    ###################################################################
    # SOCIAL
    #
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
        targets = ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == False, ProviderNetworkConnection.rejected == False).count()
        
        return targets
    
    
    def get_provider_network_pending(self):     
        targets = ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == False, ProviderNetworkConnection.rejected == False).fetch()
        
        providers = []
        for connect in targets:
            providers.append(connect.source_provider.get())

        return providers

    def get_provider_network_rejecter_count(self):     
        targets = ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == False, ProviderNetworkConnection.rejected == True).count()
        
        return targets

    def get_provider_network_rejectee_count(self):     
        sources = ProviderNetworkConnection.query(ProviderNetworkConnection.source_provider == self.key, ProviderNetworkConnection.confirmed == False, ProviderNetworkConnection.rejected == True).count()
        
        return sources


    def get_provider_network_rejected(self):     
        targets = ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == False, ProviderNetworkConnection.rejected == True).fetch()
        
        providers = []
        for connect in targets:
            providers.append(connect.source_provider.get())

        return providers

    def get_provider_network_pending_connections_source(self):     
        return ProviderNetworkConnection.query(ProviderNetworkConnection.source_provider == self.key, ProviderNetworkConnection.confirmed == False, ProviderNetworkConnection.rejected == False).fetch()

    
    def get_provider_network_pending_connections(self):     
        return ProviderNetworkConnection.query(ProviderNetworkConnection.target_provider == self.key, ProviderNetworkConnection.confirmed == False, ProviderNetworkConnection.rejected == False).fetch()
        

    ###########
    ## Views
    def get_profile_views_past_30_days(self):
        page = '/' + self.vanity_url
        today_minus_30_days = datetime.today() - timedelta(days=30)
        return SiteLog.query(SiteLog.page == page, SiteLog.access_time > today_minus_30_days).count()

    def get_profile_views_total(self):
        page = '/' + self.vanity_url
        return SiteLog.query(SiteLog.page == page).count()
