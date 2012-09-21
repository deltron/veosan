from handler import contact, static
from webapp2 import Route


# booking stuff


def get_routes():
    return [
                   Route('/contact', contact.ContactHandler),
                   # Static Pages
                   Route('/about', handler=static.StaticHandler, handler_method='get_about'),
                   Route('/careers', handler=static.StaticHandler, handler_method='get_careers'),
                   Route('/terms', handler=static.StaticHandler, handler_method='get_terms'),
                   Route('/privacy', handler=static.StaticHandler, handler_method='get_privacy'),
                   Route('/tour', handler=static.StaticHandler, handler_method='get_tour'),
                   Route('/blog', handler=static.BlogHandler),
                   Route('/browserupgrade', handler=static.StaticHandler, handler_method='get_browser_upgrade'),

       ]