from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, DomainRoute
from handler import static, admin, provider, language, tasks, prospect
import patient_routes, provider_routes, admin_routes, user_routes, public_routes, prospect_routes
from handler.provider_pkg import network_handler
from handler.booking_pkg import display_schedule_handler,\
    booking_details_handler
from handler.user_pkg.user_base_handler import InviteHandler
from handler.user_pkg.password_handler import PasswordHandler,\
    ResetPasswordHandler, ClaimHandler
import util


def build_domain_regex():
    start = 'www.<domain:((?!'
    middle = "|".join(util.DOMAINS)   
    middle.replace(".", "\.")
    end = ').)*$>'
    
    regex = r''.join(start + middle + end)
    return regex

def create_routes():
    routes = []
    routes.extend([
           # handle custom domains
           # match everything that is not veosan.com
           DomainRoute(build_domain_regex(), [                                        
              Route('/', handler=static.DomainDispatcher)
           ]),
           
           # GAE Warmup Requests
           Route('/_ah/warmup', static.WarmupHandler),
           
           # robots.txt and sitemap.xml for search engines
           Route('/robots.txt', static.RobotsHandler),
           Route('/sitemap.xml', static.SitemapHandler),
           
           # General pages
           Route('/', static.IndexHandler),
           Route('/en', static.IndexHandler, handler_method='get_en'),
           Route('/fr', static.IndexHandler, handler_method='get_fr'),
           Route('/hideside/<what>', static.HideSideHandler),

           ])
    
    routes.extend(patient_routes.get_routes())
    routes.extend(provider_routes.get_routes())
    routes.extend(admin_routes.get_routes())
    routes.extend(user_routes.get_routes())
    
    # public en
    routes.append(PathPrefixRoute('/en', public_routes.get_routes()))
    
    # public fr
    routes.append(PathPrefixRoute('/fr', public_routes.get_routes()))
    
    # prospect routes
    routes.extend(prospect_routes.get_routes())
    
    routes.extend([# invitations
               Route('/invite/<invite_token>', InviteHandler),
               Route('/claim/<token>', ClaimHandler),

               # user
               PathPrefixRoute('/user', [
                    Route('/password/<token>', PasswordHandler),
                    Route('/resetpassword', ResetPasswordHandler),
                    Route('/resetpassword/<token>', handler=ResetPasswordHandler),
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
               
               # prospect
               PathPrefixRoute('/p', [
                    Route('/<prospect_id>', handler=prospect.ProspectHandler),
               ]),
               
               # Public profile
               Route('/<vanity_url>', handler=provider.ProviderPublicProfileHandler),
               Route('/<vanity_url>/', handler=provider.ProviderPublicProfileHandler),
               
               # Display schedule
               Route('/<vanity_url>/book', display_schedule_handler.BookFromPublicProfileDisplaySchedule),
               Route('/<vanity_url>/book/date/<start_date>', display_schedule_handler.BookFromPublicProfileDisplaySchedule),
               
               # Actual booking & registration
               Route('/<vanity_url>/book/<book_date:\d{4}-\d{2}-\d{2}>/<book_hour:\d{1,2}>/<book_minutes:\d{1,2}>', booking_details_handler.BookFromPublicProfileDetails),
               Route('/<vanity_url>/book/details', booking_details_handler.BookFromPublicProfileDetails),
               Route('/<vanity_url>/book/patient', booking_details_handler.BookFromPublicProfileNewPatient),

               # Social network
               Route('/<vanity_url>/connect', network_handler.ProviderConnectHandler)]
    )
    return routes
