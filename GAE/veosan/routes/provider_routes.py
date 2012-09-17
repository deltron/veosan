#provider routes
from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import patient, provider
from handler.provider_pkg import welcome_handler, network_handler,\
    profile_handler, cv_handler, schedule_handler, address_handler
from handler.payment_pkg import payment_handler


def get_routes():
    return [

                   PathPrefixRoute('/provider', [
                       # display a status message to the provider (new, reset, etc)                                            PathPrefixRoute('/profile', [
                       PathPrefixRoute('/message', [
                           Route('/<msg_key>/<vanity_url>', welcome_handler.ProviderMessageHandler),
                       ]),
            
                       PathPrefixRoute('/welcome', [
                           Route('/<vanity_url>', welcome_handler.WelcomeHandler),
                           Route('/<vanity_url>/<disable>', welcome_handler.WelcomeHandler),
                       ]),
                                                
                       Route('/bookings/<vanity_url>', provider.ProviderBookingsHandler),
                       
                       PathPrefixRoute('/network', [
                           Route('/<vanity_url>', network_handler.ProviderNetworkHandler),
                           Route('/<vanity_url>/<operation>', network_handler.ProviderNetworkHandler),
                           Route('/<vanity_url>/<operation>/<provider_key>', network_handler.ProviderNetworkHandler),
                       ]),
                                                
                       # provider profile
                       PathPrefixRoute('/profile', [
                           Route('/<vanity_url>', profile_handler.ProviderEditProfileHandler),
                           Route('/photo/<vanity_url>', profile_handler.ProviderProfilePhotoUploadHandler),
                       ]),
            
                       # CV sections (Education, Work Experience)
                       PathPrefixRoute('/cv', [
                           Route('/<vanity_url>', cv_handler.ProviderCVHandler),
                           Route('/<section>/<vanity_url>/<operation>', cv_handler.ProviderCVHandler),
                           Route('/<section>/<vanity_url>/<operation>/<key>', cv_handler.ProviderCVHandler),
                       ]),
                       
                       # Schedule
                       PathPrefixRoute('/schedule', [
                           Route('/<vanity_url>', schedule_handler.ProviderScheduleHandler),
                           Route('/<vanity_url>/<operation>', schedule_handler.ProviderScheduleHandler),
                           Route('/<vanity_url>/<operation>/<day>/<start_time>', schedule_handler.ProviderScheduleHandler),
                           Route('/<vanity_url>/<operation>/<key>', schedule_handler.ProviderScheduleHandler),
                           
                       ]),
                                                                                                                                                              
                       # Address
                       PathPrefixRoute('/address', [
                           Route('/<vanity_url>', address_handler.ProviderEditAddressHandler),
                           Route('/change_url/<vanity_url>', address_handler.ProviderChangeURLHandler),
                       ]),
            
                       # terms display
                       #Route('/terms/<vanity_url>', user.ProviderTermsHandler),
                       
                       # upgrade account
                       Route('/upgrade/<vanity_url>', welcome_handler.ProviderUpgradeHandler),
                   ])
            ]