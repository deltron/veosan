#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from itertools import chain
from webapp2_extras.i18n import lazy_gettext as _
from markdown2 import markdown2
import logging
from utilities.time import get_days_of_the_week
from datetime import time, datetime, timedelta
from webapp2_extras.i18n import to_local_timezone
import json
import data

DEV_SERVERS = ('localhost:8080', 'veosan-stage.appspot.com')
PRODUCTION_SERVERS = ('www.veosan.com')
DOMAINS = ('veosan.com', 'veonature.com')

BOOKING_ENABLED = False

DEFAULT_LANG = 'en'
LANGUAGES = { 'en', 'fr' }
LANGUAGE_LABELS = { 'fr' : u'Français', 'en': u'English'}

# String used on many pages
saved_message = _(u'Your changes were saved.')

def is_dev_server(request):
    return request.host in DEV_SERVERS    

def get_all_provinces():
    return [('ab', _('Alberta')),
            ('bc', _('British Columbia')),
            ('mb', _('Manitoba')),
            ('nb', _('New Brunswick')),
            ('nl', _('Newfoundland and Labrador')),
            ('ns', _('Nova Scotia')),
            ('nt', _('Northwest Territories')),
            ('nu', _('Nunavut')),
            ('on', _('Ontario')),
            ('pe', _('Prince Edward Island')),
            ('qc', _('Quebec')),
            ('sk', _('Saskatchewan')),
            ('yt', _('Yukon Territory')),
        ]

def get_all_provinces_sorted():
    return massage_list(get_all_provinces())


# TODO refactor these into a common method
def get_all_categories_all_domains():
    domain_setups = data.db.get_all_domain_setup()
    if domain_setups:
        all_categories = []
        for domain in domain_setups:
            all_categories.extend(get_all_categories(domain.domain_name))
        
        return all_categories

def get_all_specialties_all_domains():
    domain_setups = data.db.get_all_domain_setup()
    if domain_setups:
        all_specialties = []
        for domain in domain_setups:
            all_specialties.extend(get_all_specialties(domain.domain_name))
        
        return all_specialties

def get_all_associations_all_domains():
    domain_setups = data.db.get_all_domain_setup()
    if domain_setups:
        all_associations = []
        for domain in domain_setups:
            all_associations.extend(get_all_associations(domain.domain_name))
        
        return all_associations

def get_all_certifications_all_domains():
    domain_setups = data.db.get_all_domain_setup()
    if domain_setups:
        all_certifications = []
        for domain in domain_setups:
            all_certifications.extend(get_all_certifications(domain.domain_name))
        
        return all_certifications


def get_all_categories(domain = None):
    domain_setup = data.db.get_domain_setup(domain)
    if domain_setup and domain_setup.categories_json:
        categories_json = domain_setup.categories_json
        categories_from_json = json.loads(categories_json)
        
        categories = []
        for (key, english_string) in categories_from_json:
            lazy_eval_tuple = (key, _(english_string))
            categories.append(lazy_eval_tuple)
        
        return categories
    else:
        return []

def get_all_categories_for_profile_editing(domain = None):
    return massage_list(get_all_categories(domain))

def massage_list(l):
    ''' Massage a list for display by:
            1. sorting in alphabetical order of display language
            2. add empty to start of list
            3. add Other at the end
    '''
    l = sort_list(l)
    l = add_nothing_at_start(l)
    l = add_other_at_end(l)
    return l

def sort_list(l):
    ''' sort labels by alphabetical order in display language '''
    l.sort(key=lambda x: x[1])
    return l

def add_nothing_at_start(l):
    l.insert(0, ("nothing", ""))
    return l

def add_other_at_end(l):
    l.extend([("other", _(u"Other"))])
    return l



# key, value
def get_all_specialties(domain = None):
    domain_setup = data.db.get_domain_setup(domain)
    if domain_setup and domain_setup.specialties_json:
        specialties_json = domain_setup.specialties_json
        specialties_from_json = json.loads(specialties_json)
        
        specialties = []
        for (key, english_string) in specialties_from_json:
            lazy_eval_tuple = (key, _(english_string))
            specialties.append(lazy_eval_tuple)
        
        return specialties
    else:
        return []

def get_all_specialties_for_form(domain = None):
    return massage_list(get_all_specialties(domain))


def get_all_titles():
    return [
            ("mr", _('Mr.')),
            ("mrs", _('Mrs.')),
            ("ms", _('Ms.')),
            ("dr", _('Dr.')),
            ]
    
def get_all_degrees():
    return [
            ("dec", _(u"Technical (DEC)")),
            ("bachelor", _(u"Bachelor's")),
            ("masters", _(u"Master's")),
            ("phd", _(u"Doctor (Ph.D)")),
            ("md", _(u"Doctor (MD)")),
        ]

def get_all_continuing_education_types():
    return [("conference", _(u"Conference")),
            ("training", _(u"Training")),
            ("presentation", _(u"Presentation")),
            ("committee", _(u"Committee")),
        ]

def get_all_durations():
    return [(0, ""),
            (15, _(u"15 minutes")),
            (30, _(u"30 minutes")),
            (45, _(u"45 minutes")),
            (60, _(u"60 minutes")),
            (75, _(u"75 minutes")),
            (90, _(u"90 minutes")),
            (105, _(u"105 minutes")),
            (120, _(u"120 minutes")),
        ]


def get_all_associations(domain = None):
    domain_setup = data.db.get_domain_setup(domain)
    if domain_setup and domain_setup.associations_json:
        associations_json = domain_setup.associations_json
        associations_from_json = json.loads(associations_json)
        
        associations = []
        for (key, english_string) in associations_from_json:
            lazy_eval_tuple = (key, _(english_string))
            associations.append(lazy_eval_tuple)
        
        return associations
    else:
        return []

def get_all_organizations_for_form(domain = None):
    return massage_list(get_all_associations(domain))

def get_all_certifications(domain = None):
    domain_setup = data.db.get_domain_setup(domain)
    if domain_setup and domain_setup.certifications_json:
        certifications_json = domain_setup.certifications_json
        certifications_from_json = json.loads(certifications_json)
        
        certifications = []
        for (key, english_string) in certifications_from_json:
            lazy_eval_tuple = (key, _(english_string))
            certifications.append(lazy_eval_tuple)
        
        return certifications
    else:
        return []

def get_all_certifications_for_form(domain = None):
    return massage_list(get_all_certifications(domain))


def getAllSites():
    return [("onsite", _(u"I am willing to do on-site visits")),
            ("clinic", _(u"I have a clinic patients can visit")),
        ]

def get_all_spoken_languages():
    return [
           # ("ar", _(u"Arabic")),
           # ("cn", _(u"Chinese")),
            ("en", _(u"English")),
            ("fr", _(u"French")),
           # ("gr", _(u"Greek")),
           # ("it", _(u"Italian")),
           # ("pt", _(u"Portuguese")),            
           # ("es", _(u"Spanish")),
           # ("ro", _(u"Romanian")),            
           # ("vn", _(u"Vietnamese")),
        ]

def get_all_profile_languages():
    return [
            ("en", _(u"English")),
            ("fr", _(u"French")),
        ]


def getAllInsurance():
    insurance = [("private", _(u"Private insurance (ex: employer)")),
            ("public", _(u"Public insurance (ex: CSST, SAAQ)")),
        ]
    insurance = massage_list(insurance)
    insurance.extend([ 
            ("dontknow", _(u"Not sure or don't know")),
            ("noanswer", _(u"Prefer not to answer"))
        ])
    return insurance

def get_signup_roles():
    return [("patient", _(u"I'm a patient")),
            ("provider", _(u"I'm health care professional")),
            ("other", _(u"Other"))]

def get_all_months():
    return [
            ("jan", _(u"January")),
            ("feb", _(u"February")),
            ("mar", _(u"March")),
            ("apr", _(u"April")),
            ("may", _(u"May")),
            ("jun", _(u"June")),
            ("jul", _(u"July")),
            ("aug", _(u"August")),
            ("sep", _(u"September")),
            ("oct", _(u"October")),
            ("nov", _(u"November")),
            ("dec", _(u"December")),
            ]

def get_all_countries():
    return [
        ('AF', 'Afghanistan'),
        ('AL', 'Albania'),
        ('DZ', 'Algeria'),
        ('AS', 'American Samoa'),
        ('AD', 'Andorra'),
        ('AO', 'Angola'),
        ('AI', 'Anguilla'),
        ('AQ', 'Antarctica'),
        ('AG', 'Antigua And Barbuda'),
        ('AR', 'Argentina'),
        ('AM', 'Armenia'),
        ('AW', 'Aruba'),
        ('AU', 'Australia'),
        ('AT', 'Austria'),
        ('AZ', 'Azerbaijan'),
        ('BS', 'Bahamas'),
        ('BH', 'Bahrain'),
        ('BD', 'Bangladesh'),
        ('BB', 'Barbados'),
        ('BY', 'Belarus'),
        ('BE', 'Belgium'),
        ('BZ', 'Belize'),
        ('BJ', 'Benin'),
        ('BM', 'Bermuda'),
        ('BT', 'Bhutan'),
        ('BO', 'Bolivia'),
        ('BA', 'Bosnia And Herzegowina'),
        ('BW', 'Botswana'),
        ('BV', 'Bouvet Island'),
        ('BR', 'Brazil'),
        ('BN', 'Brunei Darussalam'),
        ('BG', 'Bulgaria'),
        ('BF', 'Burkina Faso'),
        ('BI', 'Burundi'),
        ('KH', 'Cambodia'),
        ('CM', 'Cameroon'),
        ('CA', 'Canada'),
        ('CV', 'Cape Verde'),
        ('KY', 'Cayman Islands'),
        ('CF', 'Central African Rep'),
        ('TD', 'Chad'),
        ('CL', 'Chile'),
        ('CN', 'China'),
        ('CX', 'Christmas Island'),
        ('CC', 'Cocos Islands'),
        ('CO', 'Colombia'),
        ('KM', 'Comoros'),
        ('CG', 'Congo'),
        ('CK', 'Cook Islands'),
        ('CR', 'Costa Rica'),
        ('CI', 'Cote D`ivoire'),
        ('HR', 'Croatia'),
        ('CU', 'Cuba'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),
        ('DJ', 'Djibouti'),
        ('DM', 'Dominica'),
        ('DO', 'Dominican Republic'),
        ('TP', 'East Timor'),
        ('EC', 'Ecuador'),
        ('EG', 'Egypt'),
        ('SV', 'El Salvador'),
        ('GQ', 'Equatorial Guinea'),
        ('ER', 'Eritrea'),
        ('EE', 'Estonia'),
        ('ET', 'Ethiopia'),
        ('FK', 'Falkland Islands (Malvinas)'),
        ('FO', 'Faroe Islands'),
        ('FJ', 'Fiji'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('GF', 'French Guiana'),
        ('PF', 'French Polynesia'),
        ('TF', 'French S. Territories'),
        ('GA', 'Gabon'),
        ('GM', 'Gambia'),
        ('GE', 'Georgia'),
        ('DE', 'Germany'),
        ('GH', 'Ghana'),
        ('GI', 'Gibraltar'),
        ('GR', 'Greece'),
        ('GL', 'Greenland'),
        ('GD', 'Grenada'),
        ('GP', 'Guadeloupe'),
        ('GU', 'Guam'),
        ('GT', 'Guatemala'),
        ('GN', 'Guinea'),
        ('GW', 'Guinea-bissau'),
        ('GY', 'Guyana'),
        ('HT', 'Haiti'),
        ('HN', 'Honduras'),
        ('HK', 'Hong Kong'),
        ('HU', 'Hungary'),
        ('IS', 'Iceland'),
        ('IN', 'India'),
        ('ID', 'Indonesia'),
        ('IR', 'Iran'),
        ('IQ', 'Iraq'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IT', 'Italy'),
        ('JM', 'Jamaica'),
        ('JP', 'Japan'),
        ('JO', 'Jordan'),
        ('KZ', 'Kazakhstan'),
        ('KE', 'Kenya'),
        ('KI', 'Kiribati'),
        ('KP', 'Korea (North)'),
        ('KR', 'Korea (South)'),
        ('KW', 'Kuwait'),
        ('KG', 'Kyrgyzstan'),
        ('LA', 'Laos'),
        ('LV', 'Latvia'),
        ('LB', 'Lebanon'),
        ('LS', 'Lesotho'),
        ('LR', 'Liberia'),
        ('LY', 'Libya'),
        ('LI', 'Liechtenstein'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('MO', 'Macau'),
        ('MK', 'Macedonia'),
        ('MG', 'Madagascar'),
        ('MW', 'Malawi'),
        ('MY', 'Malaysia'),
        ('MV', 'Maldives'),
        ('ML', 'Mali'),
        ('MT', 'Malta'),
        ('MH', 'Marshall Islands'),
        ('MQ', 'Martinique'),
        ('MR', 'Mauritania'),
        ('MU', 'Mauritius'),
        ('YT', 'Mayotte'),
        ('MX', 'Mexico'),
        ('FM', 'Micronesia'),
        ('MD', 'Moldova'),
        ('MC', 'Monaco'),
        ('MN', 'Mongolia'),
        ('MS', 'Montserrat'),
        ('MA', 'Morocco'),
        ('MZ', 'Mozambique'),
        ('MM', 'Myanmar'),
        ('NA', 'Namibia'),
        ('NR', 'Nauru'),
        ('NP', 'Nepal'),
        ('NL', 'Netherlands'),
        ('AN', 'Netherlands Antilles'),
        ('NC', 'New Caledonia'),
        ('NZ', 'New Zealand'),
        ('NI', 'Nicaragua'),
        ('NE', 'Niger'),
        ('NG', 'Nigeria'),
        ('NU', 'Niue'),
        ('NF', 'Norfolk Island'),
        ('MP', 'Northern Mariana Islands'),
        ('NO', 'Norway'),
        ('OM', 'Oman'),
        ('PK', 'Pakistan'),
        ('PW', 'Palau'),
        ('PA', 'Panama'),
        ('PG', 'Papua New Guinea'),
        ('PY', 'Paraguay'),
        ('PE', 'Peru'),
        ('PH', 'Philippines'),
        ('PN', 'Pitcairn'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('PR', 'Puerto Rico'),
        ('QA', 'Qatar'),
        ('RE', 'Reunion'),
        ('RO', 'Romania'),
        ('RU', 'Russian Federation'),
        ('RW', 'Rwanda'),
        ('KN', 'Saint Kitts And Nevis'),
        ('LC', 'Saint Lucia'),
        ('VC', 'St Vincent/Grenadines'),
        ('WS', 'Samoa'),
        ('SM', 'San Marino'),
        ('ST', 'Sao Tome'),
        ('SA', 'Saudi Arabia'),
        ('SN', 'Senegal'),
        ('SC', 'Seychelles'),
        ('SL', 'Sierra Leone'),
        ('SG', 'Singapore'),
        ('SK', 'Slovakia'),
        ('SI', 'Slovenia'),
        ('SB', 'Solomon Islands'),
        ('SO', 'Somalia'),
        ('ZA', 'South Africa'),
        ('ES', 'Spain'),
        ('LK', 'Sri Lanka'),
        ('SH', 'St. Helena'),
        ('PM', 'St.Pierre'),
        ('SD', 'Sudan'),
        ('SR', 'Suriname'),
        ('SZ', 'Swaziland'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('SY', 'Syrian Arab Republic'),
        ('TW', 'Taiwan'),
        ('TJ', 'Tajikistan'),
        ('TZ', 'Tanzania'),
        ('TH', 'Thailand'),
        ('TG', 'Togo'),
        ('TK', 'Tokelau'),
        ('TO', 'Tonga'),
        ('TT', 'Trinidad And Tobago'),
        ('TN', 'Tunisia'),
        ('TR', 'Turkey'),
        ('TM', 'Turkmenistan'),
        ('TV', 'Tuvalu'),
        ('UG', 'Uganda'),
        ('UA', 'Ukraine'),
        ('AE', 'United Arab Emirates'),
        ('UK', 'United Kingdom'),
        ('US', 'United States'),
        ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
        ('VU', 'Vanuatu'),
        ('VA', 'Vatican City State'),
        ('VE', 'Venezuela'),
        ('VN', 'Viet Nam'),
        ('VG', 'Virgin Islands (British)'),
        ('VI', 'Virgin Islands (U.S.)'),
        ('EH', 'Western Sahara'),
        ('YE', 'Yemen'),
        ('YU', 'Yugoslavia'),
        ('ZR', 'Zaire'),
        ('ZM', 'Zambia'),
        ('ZW', 'Zimbabwe')
    ]

def get_all_countries_for_form():
    return massage_list(get_all_countries())


''' dump properties '''
def dump(obj):  
    return vars(obj)
    # todo split at the comma (replace with <br>)
  

#list of list of tuples
CODE_TUPLES_LIST = [ ]

# Flat tuple list
CODE_TUPLES = list(chain.from_iterable(CODE_TUPLES_LIST))

# dictionary of all codes: string
CODE_DICT = dict(CODE_TUPLES)

# hack for translations
CODE_DICT_PER_LANG = dict()

def create_untranslated_code_tuple_list():
    code_tuples_list = []
    code_tuples_list.append(get_all_categories_all_domains())
    code_tuples_list.append(get_all_specialties_all_domains())
    code_tuples_list.append(get_all_associations_all_domains())
    code_tuples_list.append(get_all_certifications_all_domains())
    code_tuples_list.append(get_all_categories_for_profile_editing())
    code_tuples_list.append(get_all_degrees())
    code_tuples_list.append(get_all_continuing_education_types())
    code_tuples_list.append(get_all_titles())
    code_tuples_list.append(get_all_provinces())

    # more...
    
    # flatten
    code_tuples = list(chain.from_iterable(code_tuples_list))
    code_dict = dict(code_tuples)
    return code_dict
    
    

def code_to_string(code):
    '''
        Catch all function to convert code to human string coverter
    '''
    # Check cache for codes dict (hack for lazy translation)
    lang = _('en')
    if not CODE_DICT_PER_LANG.has_key(lang):
        new_code_dict = create_untranslated_code_tuple_list()
        CODE_DICT_PER_LANG[lang] = new_code_dict
    # get code_dict for language
    lang_code_dict = CODE_DICT_PER_LANG[lang]
    value = code
    if lang_code_dict.has_key(code):
        value = lang_code_dict[code]
    return value

def remove_empty_strings_from_list(l):
    return filter (lambda a: a != u'', l)

def markdown(text):
    if text:
        return markdown2.markdown(text)

note_types = ['call', 'email', 'meeting', 'info', 'admin']

def get_all_note_types():
    return [('call', _(u'Call')),
            ('email', _(u'Email')),
            ('meeting', _(u'Meeting')),
            ('info', _(u'Info')),
            ('admin', _(u'Admin')),
            ]
    
# List of provider status
provider_statuses = ['prospect', 'contacted_phone', 'contacted_meeting', 'client_enabled', 'client_suspended', 'ex_client_disabled']
prospect_tags = ['new', 'potential_champion', 'generic_person', 'unlikely', 'requires_followup', 'hot', 'warm', 'cold']
employment_tags = ['professor', 'hospital', 'clinic_small', 'clinic_big', 'independent']


def get_all_employment_tags():
    employment_tag_choices = map(lambda s: (s, _(s.capitalize())), employment_tags)
    return employment_tag_choices

def get_all_prospect_tags():
    status_choices = map(lambda s: (s, _(s.capitalize())), prospect_tags)
    return status_choices

def get_all_status_types():
    status_choices = map(lambda s: (s, _(s.capitalize())), provider_statuses)
    return status_choices

class ScheduleMap(dict):
    '''
        Map of schedules keyed by day and start hour to simplify display
    '''
    
    def within_span(self, day_key, hour_key):
        '''
            Check if a day/hour intersect in within the continuation of a schedule starting earlier
        '''
        day_schedules = self[day_key]
        for key in day_schedules.keys():
            s = day_schedules[key]
            if (hour_key >= s.start_time) & (hour_key < s.end_time):
                return True 
        # if no schedules match return false
        return False
    

def create_schedule_dict(schedules):
    sm = ScheduleMap()
    for (key, label) in get_days_of_the_week():
        sm[key] = dict()
    for s in schedules:
        sm[s.day][s.start_time] = s
    logging.debug('smm %s' % sm)
    return sm


def generate_datetimes_from_schedule(schedule, date):
    datetimes = []
    t = schedule.start_time
    while t < schedule.end_time:
        dt = datetime.combine(date, time(hour=t))
        datetimes.append(dt)
        t = t+1
    return datetimes
    

def generate_complete_datetimes_dict(schedules, start_date, period):
    '''
        Generate a dict of all dates in the period to list of hours available
    '''
    dtm = dict()
    # create a dist [day_key][start_time] = schedule
    sm = create_schedule_dict(schedules)
    end_date = start_date + period
    d = start_date
    while d < end_date:
        dtm[d] = []
        # day of week
        weekday_int = d.weekday()
        # map the number to the actual day
        day_key = get_days_of_the_week()[weekday_int][0]
        # check schedules for that day
        days_schedules = sm[day_key]
        for hour_key in sorted(days_schedules.keys()):
            s = days_schedules[hour_key]
            datetimes_list = generate_datetimes_from_schedule(s, d)
            dtm[d].extend(datetimes_list)
        d = d + timedelta(days=1)
    return dtm
    
    
def remove_confirmed_bookings_from_schedule(schedule_dict, bookings):
    '''
        Remove all bookings from schedule dict
    '''
    for b in bookings:
        # convert booking datetime to local timezone
        booking_datetime = to_local_timezone(b.datetime)
        booking_date = booking_datetime.date()
        if schedule_dict.has_key(booking_date):
            day_datetimes = schedule_dict[booking_date]
            tz = booking_datetime.tzinfo
            logging.info('tzinfo: %s' % tz)
            day_datetimes = map(lambda t: t.replace(tzinfo=tz), day_datetimes)
            if booking_datetime in day_datetimes:
                day_datetimes.remove(booking_datetime)
                schedule_dict[booking_date] = day_datetimes
                logging.info('removed %s from %s' % (booking_datetime, schedule_dict[booking_date]))
    return schedule_dict
