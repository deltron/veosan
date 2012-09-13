#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from itertools import chain
from webapp2_extras.i18n import lazy_gettext as _
from markdown2 import markdown2
import logging
from utilities.time import get_days_of_the_week
from datetime import time, datetime, timedelta
from webapp2_extras.i18n import to_local_timezone

DEV_SERVERS = ('localhost:8080', 'veosan-stage.appspot.com')
PRODUCTION_SERVERS = ('www.veosan.com')

BOOKING_ENABLED = False

DEFAULT_LANG = 'fr'
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

def get_all_categories():
    return [
            ("chiropractor", _(u"Chiropractor")),
            ("doctor", _('Doctor')),
            ("administration", _(u"Health Care Administration")),
            ("osteopath", _(u"Osteopath")),
            ("occupational_therapy", _('Occupational Therapist')),
            ("nurse", _('Nurse')),
            ("auxiliary_nurse", _(u"Auxiliary Nurse")),
            ("physiotherapy", _(u"Physiotherapist")),
            ("psychology", _(u"Psychologist")),
            ("podiatrist", _('Podiastrist')),
            ("kinesiology", _('Kinesiology')),
            ("dentist", _('Dentist')),
            ("dietitian", _('Dietitian')),
            ("nutritionist", _('Nutritionist')),
            ("optometrist", _('Optometrist')),
            ("denturologist", _('Denturist')),
        ]

def get_all_categories_for_profile_editing():
    return massage_list(get_all_categories())

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
def get_all_specialties():
    return [("sports", _(u"Sports")),
            ("geriatric", _(u"Geriatric")),
            ("cardiology", _(u"Cardiology")),
            ("pneumology", _(u"Pneumology")),
            ("orthopedic", _(u"Orthopedic")),
            ("neurology", _(u"Neurology")),
            ("pediatric", _(u"Pediatric")),
            ("vestibular_rehabilitation", _(u"Vestibular Rehabilitation")),
            ("womens_health", _(u"Women's Health"))
        ]

def get_all_specialties_for_form():
    return massage_list(get_all_specialties())


def getAllSpecialitiesForPatient():
    specialty_list = massage_list(get_all_specialties())
    specialty_list.extend([ 
            ("dontknow", _(u"Not sure or don't know")),
            ("noanswer", _(u"Prefer not to answer"))
        ])
    return specialty_list

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

def getAllAssociations():
    return [("oppq", _(u"Ordre professionnel de la physiotherapie du Quebec (OPPQ)")),
            ("acq", _(u"Association des chiropraticiens du Québec (ACQ)")),
            ("cca", _(u"Canadian Chiropractic Association (CCA)")),
            ("cma", _(u"Canadian Medical Association (CMA)")),
            ("fmrq", _(u"Fédération des médecins résidents du Québec (FMRQ)")),
            ("cpa", _(u"Canadian Physiotherapy Association (CPA)")),
            ("campt", _(u"Canadian Academy of Manipulative Physiotherapy (CAMPT)")),
            ("oiiq", _(u"Ordre des infirmières et infirmiers du Québec (OIIQ)")),
            ("odq_denture", _(u"L’Ordre des denturologistes du Québec (ODQ)")),
            ("odq", _(u"Ordre des dentistes du Québec (ODQ)")),
            ("dc", _(u"Dietitians of Canada (DC)")),
            ("opdq", _(u"Ordre professionnel des diététistes du Québec (OPDQ)")),
            ("cao", _(u"Canadian Association of Optometrists (CAO)")),
            ("aoq", _(u"L'Association des optométristes du Québec (AOQ)")),
        ]

def get_all_organizations_for_form():
    return massage_list(getAllAssociations())

def getAllCertifications():
    return [("mckenzie", _(u"McKenzie Method")),
            ("art", _(u"Active Release Therapy (ART)")),
        ]

def get_all_certifications_for_form():
    return massage_list(getAllCertifications())


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
    code_tuples_list.append(get_all_categories())
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

note_types = ['call', 'email', 'meeting', 'info']

def get_all_note_types():
    return [('call', _(u'Call')),
            ('email', _(u'Email')),
            ('meeting', _(u'Meeting')),
            ('info', _(u'Info'))]
    
# List of provider status
provider_statuses = ['prospect', 'contacted_phone', 'contacted_meeting', 'client_enabled', 'client_suspended', 'ex_client_disabled']

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
