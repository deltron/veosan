from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import admin, provider_admin

admin_routes = [PathPrefixRoute('/admin', [
                   Route('/bookings', admin.AdminBookingsHandler),
                   Route('/booking/<operation>/<bk>', admin.AdminBookingDetailHandler),
                   Route('/providers', admin.AdminProvidersHandler),
                   Route('/patients', admin.AdminPatientsHandler),
                   Route('/invites', admin.AdminInvitesHandler),
                   Route('/dashboard', admin.AdminDashboardHandler),
                   Route('/data', admin.AdminDataHandler),
                   Route('/data/stage', admin.AdminStageDataHandler),
                   Route('/data/delete', admin.AdminDeleteDataHandler),
            
                   Route('/site_config/<feature>', admin.AdminSiteConfigHandler),
            
                   PathPrefixRoute('/provider', [
                       # provider actions
                       Route('/status', provider_admin.ProviderStatusHandler),
                                                                          
                       # provider admin
                       Route('/admin/<vanity_url>', provider_admin.ProviderAdministrationHandler),
                    
                       # custom domain
                       Route('/domain/<vanity_url>', provider_admin.ProviderDomainHandler),
                    
                       # logs
                       Route('/logs/<vanity_url>', provider_admin.ProviderEventLogHandler),
            
                       Route('/notes/<vanity_url>', provider_admin.ProviderNotesHandler),
                       Route('/notes/<vanity_url>/<operation>/<note_key>', provider_admin.ProviderNotesHandler),
                       Route('/feature/<feature_switch>/<vanity_url>', provider_admin.ProviderFeaturesHandler),
                    ]),
               ]),
            ]