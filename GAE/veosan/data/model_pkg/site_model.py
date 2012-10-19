from google.appengine.ext import ndb

class SiteConfig(ndb.Model):
    booking_enabled = ndb.BooleanProperty(default=False)
    google_analytics_enabled = ndb.BooleanProperty(default=False)
    facebook_like_enabled = ndb.BooleanProperty(default=False)
    signup_enabled = ndb.BooleanProperty(default=False)
    error_email_enabled = ndb.BooleanProperty(default=False)
    welcome_email_enabled = ndb.BooleanProperty(default=False)


class SiteLog(ndb.Model):
    page = ndb.StringProperty()
    access_time = ndb.DateTimeProperty(auto_now_add=True)
    ip = ndb.StringProperty()
    referer = ndb.TextProperty()
    language = ndb.StringProperty()
    user = ndb.KeyProperty(kind='User')
    user_email = ndb.StringProperty()
    admin_email = ndb.StringProperty()
    prospect = ndb.KeyProperty(kind='ProviderProspect')
    prospect_id = ndb.StringProperty()

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
    click_full_button = ndb.IntegerProperty(default=0)
    click_preview_button = ndb.IntegerProperty(default=0)


class DomainSetup(ndb.Model):
    domain_name = ndb.StringProperty()
    brand_name = ndb.StringProperty()
    brand_name_case = ndb.StringProperty()
    css_file = ndb.StringProperty()
    categories_json = ndb.JsonProperty()
    specialties_json = ndb.JsonProperty()
    specialties_display = ndb.BooleanProperty()
    associations_json = ndb.JsonProperty()
    certifications_display = ndb.BooleanProperty()
    certifications_json = ndb.JsonProperty()
    