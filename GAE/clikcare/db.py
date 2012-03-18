'''
Created on Mar 17, 2012

@author: phil
'''

from google.appengine.ext import db

class PatientRequest(db.Model):
    '''
    A patient request to see a health-care professional
    '''
    createdOn = db.DateTimeProperty(auto_now_add=True)
    #author = db.UserProperty()
    specialty = db.StringProperty()
    location = db.StringProperty()
    when = db.StringProperty()
    who = db.StringProperty()
        