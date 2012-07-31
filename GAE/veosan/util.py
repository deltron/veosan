#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from itertools import chain
from webapp2_extras.i18n import lazy_gettext as _
from markdown2 import markdown2
import logging

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

def get_all_regions():
    return [('mtl-downtown', _(u'Montreal - Downtown')),
            ('mtl-westisland', _(u'Montreal - West-Island')),
            ('mtl-east', _(u'Montreal - East')),
            ('mtl-nord', _(u'Montreal - North')),
            ('laval', _(u'Laval')),
            ('south-shore', _(u'South Shore')),
            ('other', _(u'Other')),
            ]    
    

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
def getAllSpecialities():
    return [("sports", _(u"Sports")),
            ("geriatric", _(u"Geriatric")),
            ("cardiology", _(u"Cardiology")),
            ("pneumology", _(u"Pneumology")),
            ("orthopedic", _(u"Orthopedic")),
            ("neurology", _(u"Neurology")),
            ("pediatric", _(u"Pediatric"))
        ]
    
def getAllSpecialitiesForPatient():
    z = getAllSpecialities()
    z.extend([ 
            ("other", _(u"Other")),
            ("dontknow", _(u"Not sure or don't know")),
            ("noanswer", _(u"Prefer not to answer"))
        ])
    return z

def get_all_titles():
    return [
            ("mr", _('Mr.')),
            ("mrs", _('Mrs.')),
            ("ms", _('Ms.')),
            ("dr", _('Dr.')),
            ]

def get_all_schools():
    return [
            ("concordia", _(u"Concordia University")),
            ("mcgill", _(u"McGill University")),
            ("udem", _(u"Université de Montréal")),
            ("uqtr", _(u"Université de Québec à Trois-Rivières")),
            ("usherb", _(u"Université de Sherbrooke")),
            ("laval", _(u"Université Laval")),
        ]
    
def get_all_schools_for_form():
    return massage_list(get_all_schools())

    
def get_all_degrees():
    return [("bachelor", _(u"Bachelor's")),
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



def getAllInsurance():
    return [("private", _(u"Private insurance (ex: employer)")),
            ("public", _(u"Public insurance (ex: CSST, SAAQ)")),
            ("other", _(u"Other coverage")),
            ("dontknow", _(u"Not sure or don't know")),
            ("noanswer", _(u"Prefer not to answer"))
        ]
    
def getAllConfirmation():
    return [("email", _(u"Email")),
            ("telephone", _(u"Telephone")),
        ]


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
    code_tuples_list.append(get_all_regions())
    code_tuples_list.append(get_all_categories())
    code_tuples_list.append(get_all_categories_for_profile_editing())
    code_tuples_list.append(get_all_schools())
    code_tuples_list.append(get_all_degrees())
    code_tuples_list.append(get_all_continuing_education_types())
    code_tuples_list.append(get_all_titles())

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

note_types = ['call', 'email', 'meeting', 'admin']

def get_all_note_types():
    return [('call', _(u'Call')),
            ('email', _(u'Email')),
            ('meeting', _(u'Meeting')),
            ('admin', _(u'Admin'))]
    
# List of provider status
provider_statuses = ['prospect', 'contacted_phone', 'contacted_meeting', 'client_enabled', 'client_suspended', 'ex_client_disabled']

def get_all_status_types():
    status_choices = map(lambda s: (s, _(s.capitalize())), provider_statuses)
    return status_choices


