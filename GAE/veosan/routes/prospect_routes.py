from handler import static
from webapp2 import Route
from handler.user_pkg import signup_handler


# routes for prospects
def get_routes():
    return [
                   Route('/tour/<prospect_id>', handler=static.StaticHandler, handler_method='get_tour'),
                   Route('/blog/<prospect_id>', handler=static.BlogHandler),
                   Route('/signup/<prospect_id>', handler=signup_handler.ProviderSignupHandler2),
       ]