from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler.user_pkg import signup_handler
from handler.user_pkg.login_handler import LoginHandler, LogoutHandler



def get_routes():
    return [ PathPrefixRoute('/en/signup', [Route('/patient', signup_handler.PatientSignupHandler),
                                            Route('/provider', signup_handler.ProviderSignupHandler1),
                                            Route('/provider2', signup_handler.ProviderSignupHandler2),
               ]),
             PathPrefixRoute('/fr/signup', [Route('/patient', signup_handler.PatientSignupHandler),
                                            Route('/provider', signup_handler.ProviderSignupHandler1),
                                            Route('/provider2', signup_handler.ProviderSignupHandler2),
               ]),
               
               Route('/login', LoginHandler),
               Route('/en/login', LoginHandler, handler_method='get_en'),
               Route('/fr/login', LoginHandler, handler_method='get_fr'),
               Route('/login/<next_action>/<key>', LoginHandler),
               Route('/logout', LogoutHandler)
       
            ]
