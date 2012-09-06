from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler.user_pkg import signup_handler
from handler import user



def get_routes():
    return [ PathPrefixRoute('/signup', [Route('/patient', signup_handler.PatientSignupHandler),
                                            Route('/provider', signup_handler.ProviderSignupHandler1),
                                            Route('/provider2', signup_handler.ProviderSignupHandler2),
                                            Route('/patient/<lang_key>', signup_handler.PatientSignupHandler),
                                            Route('/provider/<lang_key>', signup_handler.ProviderSignupHandler1),
               ]),
        
               Route('/login', user.LoginHandler),
               Route('/login/<next_action>/<key>', user.LoginHandler),
               Route('/logout', user.LogoutHandler)
       
            ]
