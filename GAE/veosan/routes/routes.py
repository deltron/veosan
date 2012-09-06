from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, DomainRoute
from handler import static, user, admin, provider, language, tasks
import patient_routes, provider_routes, admin_routes, user_routes, public_routes
from handler.provider_pkg import network_handler
from handler.booking_pkg import display_schedule_handler, booking_registration_handler

def create_routes():
    routes = []
    routes.extend([
           # handle custom domains
           # match everything that is not veosan.com
           DomainRoute(r'www.<domain:((?!veosan\.com).)*$>', [                                        
              Route('/', handler=static.DomainDispatcher)
           ]),
           
           # GAE Warmup Requests
           Route('/_ah/warmup', static.WarmupHandler),
           
           # robots.txt and sitemap.xml for search engines
           Route('/robots.txt', static.RobotsHandler),
           Route('/sitemap.xml', static.SitemapHandler),
           
           # General pages
           ('/', static.IndexHandler),
           #Route('/en', static.IndexHandler, handler_method='get_en'),
           #Route('/fr', static.IndexHandler, handler_method="get_fr"),
           Route('/hideside/<what>', static.HideSideHandler),

           ])
    
    routes.extend(patient_routes.get_routes())
    routes.extend(provider_routes.get_routes())
    routes.extend(admin_routes.get_routes())
    routes.extend(user_routes.get_routes())
    
    # public 
    routes.extend(public_routes.get_routes())
    # public fr
    routes.append(PathPrefixRoute('/en', public_routes.get_routes()))
    #public en
    routes.append(PathPrefixRoute('/fr', public_routes.get_routes()))
    
    routes.extend([# invitations
               Route('/invite/<invite_token>', user.InviteHandler),

               # user
               PathPrefixRoute('/user', [
                    Route('/activation/<signup_token>', handler=user.ActivationHandler),
                    Route('/password/<signup_token>', user.PasswordHandler),
                    Route('/resetpassword', user.ResetPasswordHandler),
                    Route('/resetpassword/<resetpassword_token>', handler=user.ResetPasswordHandler),
               ]),
               
               # sales material
               Route('/sales', static.SalesHandler),
               Route('/sales/<page>', static.SalesHandler),
               
               # admin
               Route('/admin', admin.AdminIndexHandler),

               PathPrefixRoute('/tasks', [
                   Route('/mail_errors', tasks.MailErrorHandler),
               ]),
               
               Route('/lang/<lang>', language.LanguageHandler),
               Route('/lang/<lang>/<hide_side>', language.LanguageHandler),
               
               # if nothing above matches, try to find a provider
               # if this doesn't find someone it should throw a 404 (or back to index page?)
               
               # Public profile
               Route('/<vanity_url>', handler=provider.ProviderPublicProfileHandler),
               Route('/<vanity_url>/', handler=provider.ProviderPublicProfileHandler),
               
               # Display schedule
               Route('/<vanity_url>/book', display_schedule_handler.BookFromPublicProfileDisplaySchedule),
               Route('/<vanity_url>/book/date/<start_date>', display_schedule_handler.BookFromPublicProfileDisplaySchedule),
               
               # Actual booking & registration
               Route('/<vanity_url>/book/<book_date:\d{4}-\d{2}-\d{2}>/<book_time:\d{1,2}>', booking_registration_handler.BookFromPublicProfileRegistration),
               Route('/<vanity_url>/book/register', booking_registration_handler.BookFromPublicProfileRegistration),

               # Social network
               Route('/<vanity_url>/connect', network_handler.ProviderConnectHandler)]
    )
    return routes
