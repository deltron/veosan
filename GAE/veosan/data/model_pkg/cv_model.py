from google.appengine.ext import ndb


class Education(ndb.Model):  
    provider = ndb.KeyProperty(kind='Provider')
 
    start_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()

    school_name = ndb.StringProperty()
    other = ndb.StringProperty()
    location = ndb.StringProperty()

    degree_type = ndb.StringProperty()
    degree_title = ndb.StringProperty()

    description = ndb.TextProperty()


class ContinuingEducation(ndb.Model):  
    provider = ndb.KeyProperty(kind='Provider')
 
    year = ndb.IntegerProperty()
    month = ndb.IntegerProperty()

    hours = ndb.FloatProperty()

    type = ndb.StringProperty()

    title = ndb.StringProperty()

    description = ndb.StringProperty()


class Experience(ndb.Model):   
    provider = ndb.KeyProperty(kind='Provider')

    start_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()

    company_name = ndb.StringProperty()
    title = ndb.StringProperty()
    location = ndb.StringProperty()

    description = ndb.TextProperty()


class ProfessionalOrganization(ndb.Model):   
    provider = ndb.KeyProperty(kind='Provider')
    organization = ndb.StringProperty()
    other = ndb.StringProperty()
    start_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()
    location = ndb.StringProperty()
    
class ProfessionalCertification(ndb.Model):   
    provider = ndb.KeyProperty(kind='Provider')
    certification = ndb.StringProperty()
    other = ndb.StringProperty()
    year = ndb.IntegerProperty()