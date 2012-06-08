
from data.model import Provider
from datetime import date


def create_test_provider(**args):
    p = Provider(**args)
    p_key = p.put()
    return (p_key, p)
    
    
def create_test_providers():
    '''
        Create a bunch of providers for testing
    '''
    p1 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['geriatric'], associations=[''], certifications=[''], onsite=True, start_year='2001',
                  first_name='Provider', last_name='One', title='Mr.', credentials='Ph.D.', email='provider1@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")

    p2 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['sports'], associations=[''], certifications=[''], onsite=False, start_year='2003',
                  first_name='Provider', last_name='Two', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    p3 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['geriatric'], associations=[''], certifications=[''], onsite=False, start_year='2010',
                  first_name='Provider', last_name='Two', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    p4 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['geriatric'], associations=[''], certifications=[''], onsite=False, start_year='1999',
                  first_name='Provider', last_name='Two', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    p5 = create_test_provider(terms_agreement=True, terms_date=date.today(),
                  category=u'physiotherapy', specialty=['sports'], associations=[''], certifications=[''], onsite=False, start_year='1999',
                  first_name='Provider', last_name='Two', title='Mr.', credentials='M.Sc.', email='provider2@clikcare.com', phone='514-123-1234',
                  location=u'mtl-downtown', address='1234 Grand Boul.', city='Montreal', postal_code='H2J 3M7',
                  bio = "Here's my bio", quote="Here's my quote")
    
    return [p1, p2, p3, p4, p5]
    