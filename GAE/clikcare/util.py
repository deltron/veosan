#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from webapp2_extras.i18n import lazy_gettext as _

DEV_SERVERS = ('localhost:8080', 'clikcare-stage.appspot.com')

DEFAULT_LANG = 'fr'
LANGUAGE_LABELS = { 'fr' : u'Français', 'en': u'English'}

# String used on many pages
saved_message = _(u'Your changes were saved.')

def is_dev_server(request):
    return request.host in DEV_SERVERS
            

# key, value
def getAllRegions():
    return [('mtl-downtown', _(u'Montreal - Downtown')),
            ('mtl-westisland', _(u'Montreal - West-Island'))
            ]
    
## key, value
CAT_PHYSIO = "physiotherapy"
CAT_CHIRO = "chiropractor"
CAT_OSTEO = "osteopath"

def getAllCategories():
    return [(CAT_PHYSIO, _(u"Physiotherapist")),
            (CAT_CHIRO, _(u"Chiropractor")),
            (CAT_OSTEO, _(u"Osteopath"))
        ]

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


def getAllSchools():
    return [("na", _(u"Not Applicable")),
            ("concordia", _(u"Concordia University")),
            ("mcgill", _(u"McGill University")),
            ("udem", _(u"Universite de Montreal")),
            ("uqtr", _(u"Universite de Quebec a Trois-Rivieres")),
            ("usherb", _(u"Universite de Sherbrooke"))
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


''' dump properties '''
def dump(obj):  
    return vars(obj)
    # todo split at the comma (replace with <br>)
    

