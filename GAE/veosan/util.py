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
LANGUAGE_LABELS = { 'fr' : u'Français', 'en': u'English'}

# String used on many pages
saved_message = _(u'Your changes were saved.')

def is_dev_server(request):
    return request.host in DEV_SERVERS
            
def get_all_regions():
    return [('mtl-downtown', _(u'Montreal - Downtown')),
            ('mtl-westisland', _(u'Montreal - West-Island'))]    
    
## key, value
CAT_PHYSIO = "physiotherapy"
CAT_CHIRO = "chiropractor"
CAT_OSTEO = "osteopath"

def get_all_categories():
    return [(CAT_PHYSIO, _(u"Physiotherapist")),
            (CAT_CHIRO, _(u"Chiropractor")),
            (CAT_OSTEO, _(u"Osteopath"))]
           

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


def get_all_schools():
    return [("na", _(u"Not Applicable")),
            ("concordia", _(u"Concordia University")),
            ("mcgill", _(u"McGill University")),
            ("udem", _(u"Universite de Montreal")),
            ("uqtr", _(u"Universite de Quebec a Trois-Rivieres")),
            ("usherb", _(u"Universite de Sherbrooke"))
        ]
    
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
            ("cpa", _(u"Canadian Physiotherapy Association (CPA)")),
            ("campt", _(u"Canadian Academy of Manipulative Physiotherapy (CAMPT)"))
        ]

def getAllCertifications():
    return [("mckenzie", _(u"McKenzie Method")),
            ("art", _(u"Active Release Therapy (ART)"))
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
CODE_DICT_PER_LANG =  dict()

def create_untranslated_code_tuple_list():
    code_tuples_list = []
    code_tuples_list.append(get_all_regions())
    code_tuples_list.append(get_all_categories())
    code_tuples_list.append(get_all_schools())
    code_tuples_list.append(get_all_degrees())
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


