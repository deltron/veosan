
from data.model import Provider, Schedule
from datetime import date


def open_schedule(p_key):
    '''
        Add Schedule items from Monday to Friday 9-12 and 13-17
    '''
    for day in range(0, 5):
        am = Schedule(day=day, startTime=8, endTime=12, provider=p_key)
        am.put()
        pm = Schedule(day=day, startTime=13, endTime=17, provider=p_key)
        pm.put()
        
        
def create_test_provider(**args):
    '''
        Create a test provider with an open schedule
    '''
    p = Provider(**args)
    p_key = p.put()
    open_schedule(p_key)
    return (p_key, p)
    
    
def create_test_providers():
    '''
        Create a bunch of providers for testing
    '''
    p1 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['geriatric'], associations=[''], certifications=[''], onsite=True, start_year='2001',
                  first_name='Provider', last_name='One-OnSite', title='Mr.', credentials='Ph.D.', email='provider1@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")

    p2 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['sports'], associations=[''], certifications=[''], onsite=False, start_year='2003',
                  first_name='Provider', last_name='Two', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    p3 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['geriatric'], associations=[''], certifications=[''], onsite=False, start_year='2010',
                  first_name='Provider', last_name='Three', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    p4 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['geriatric'], associations=[''], certifications=[''], onsite=False, start_year='1999',
                  first_name='Provider', last_name='Four', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    p5 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['sports'], associations=[''], certifications=[''], onsite=False, start_year='1999',
                  first_name='Provider', last_name='Five', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    p6 = create_test_provider(terms_agreement=False, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['sports'], associations=[''], certifications=[''], onsite=False, start_year='1999',
                  first_name='Provider', last_name='Six-No-Terms', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    return [p1, p2, p3, p4, p5, p6]
    