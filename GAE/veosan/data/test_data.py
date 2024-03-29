
from data.model_pkg.provider_model import Provider, Schedule
from data.model_pkg.prospect_model import ProviderProspect
from datetime import date
from utilities import time

def create_test_provider(**args):
    '''
        Create a test provider with an open schedule
    '''
    p = Provider(**args)
    p_key = p.put()
    return (p_key, p)
    
    
def create_test_providers():
    '''
        Create a bunch of providers for testing
    '''
    p1 = create_test_provider(terms_agreement=True, terms_date=date.today(), status='prospect',
                  category=u'physiotherapy', associations=[''], certifications=[''], practice_sites=['onsite'], start_year='2001',
                  first_name='Provider', last_name='One-OnSite-AllWeek', title='Mr.', credentials='Ph.D.', email='provider1@veosan.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote", vanity_url='p1')
    open_schedule_all_week(p1[0])

    p2 = create_test_provider(terms_agreement=True, terms_date=date.today(), status='prospect',
                  category=u'physiotherapy', associations=[''], certifications=[''], start_year='2003',
                  first_name='Provider', last_name='Two-Weekends', title='Mr.', credentials='M.Sc.', email='provider2@veosan.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote", vanity_url='p2')
    open_schedule_weekends(p2[0])
    
    p3 = create_test_provider(terms_agreement=True, terms_date=date.today(), status='prospect',
                  category=u'physiotherapy', associations=[''], certifications=[''], start_year='2010',
                  first_name='Provider', last_name='Three', title='Mr.', credentials='M.Sc.', email='provider2@veosan.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote", vanity_url='p3')
    open_schedule_all_mornings(p3[0])
    
    p4 = create_test_provider(terms_agreement=True, terms_date=date.today(), status='prospect',
                  category=u'physiotherapy', associations=[''], certifications=[''], start_year='1999',
                  first_name='Provider', last_name='Four', title='Mr.', credentials='M.Sc.', email='provider2@veosan.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote", vanity_url='p4')
    
    p5 = create_test_provider(terms_agreement=True, terms_date=date.today(), status='prospect',
                  category=u'physiotherapy', associations=[''], certifications=[''], start_year='1999',
                  first_name='Provider', last_name='Five', title='Mr.', credentials='M.Sc.', email='provider2@veosan.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote", vanity_url='p5')
    
    p6 = create_test_provider(terms_agreement=False, terms_date=None, status='prospect',
                  category=u'physiotherapy', associations=[''], certifications=[''], start_year='1999',
                  first_name='Provider', last_name='Six-No-Terms', title='Mr.', credentials='M.Sc.', email='provider2@veosan.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote", vanity_url='p6')
    
    p7 = create_test_provider(terms_agreement=True, terms_date=date.today(), status='prospect',
                  category=u'physiotherapy', associations=[''], certifications=[''], start_year='1999',
                  first_name='Provider', last_name='Seven-Disabled', title='Mr.', credentials='M.Sc.', email='provider2@veosan.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote", vanity_url='p7')
    
    return [p1, p2, p3, p4, p5, p6, p7]


def create_prospect(**args):
    pp = ProviderProspect(**args)
    pp.put()
    

def create_test_prospects():
    for x in range(1, 25):
        create_prospect(prospect_id = 'p%s' % x, language='en', email='email%s@test.com' % x, first_name='First', last_name='%sLast' % x, category='dentist')


def open_schedule_all_week(p_key):
    '''Add Schedule items from Monday to Friday 9-12 and 13-17 '''
    for (day_key, day_name) in time.get_days_of_the_week():
        am = Schedule(day=day_key, start_time=8, end_time=12, provider=p_key)
        am.put()
        pm = Schedule(day=day_key, start_time=13, end_time=17, provider=p_key)
        pm.put()
        
        
def open_schedule_weekends(p_key):
    '''Add Schedule items from Sat and Sun 9-12 and 13-17 '''
    for day_key in ['saturday', 'sunday']:
        Schedule(day=day_key, start_time=8, end_time=12, provider=p_key).put() # AM
        Schedule(day=day_key, start_time=13, end_time=17, provider=p_key).put() # PM

    
def open_schedule_all_mornings(p_key):
    '''Add Schedule items from Sat and Sun 9-12 and 13-17 '''
    for (day_key, day_name) in time.get_days_of_the_week():
        Schedule(day=day_key, start_time=8, end_time=12, provider=p_key).put() # AM
        