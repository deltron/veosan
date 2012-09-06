from handler import contact, static
from webapp2 import Route


# booking stuff

public_routes = [
                   Route('/contact', contact.ContactHandler),
                   # Static Pages
                   Route('/about', handler=static.StaticHandler, name='about'),
                   Route('/careers', handler=static.StaticHandler, name='careers'),
                   Route('/terms', handler=static.StaticHandler, name='terms'),
                   Route('/privacy', handler=static.StaticHandler, name='privacy'),
                   Route('/tour', handler=static.StaticHandler, name='tour'),
                   Route('/blog', handler=static.BlogHandler),
       ]
