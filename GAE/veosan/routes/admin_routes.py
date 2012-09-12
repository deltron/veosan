from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import admin, provider_admin
from handler.admin_pkg import data_handler, admin_bookings_handler,\
    prospects_handler


def get_routes():
    return [PathPrefixRoute('/admin', [
                   Route('/bookings', admin_bookings_handler.AdminBookingsHandler),
                   Route('/booking/<operation>/<bk>', admin_bookings_handler.AdminBookingDetailHandler),
                   Route('/providers', admin.AdminProvidersHandler),
                   Route('/patients', admin.AdminPatientsHandler),
                   Route('/invites', admin.AdminInvitesHandler),
                   Route('/dashboard', admin.AdminDashboardHandler),
                   Route('/data', data_handler.AdminDataHandler),
                   Route('/data/stage', data_handler.AdminStageDataHandler),
                   Route('/data/delete', data_handler.AdminDeleteDataHandler),
            
                   Route('/site_config/<feature>', admin.AdminSiteConfigHandler),

                   Route('/prospects', prospects_handler.AdminProspectsHandler),
                   Route('/prospects/delete/<prospect_id>', prospects_handler.AdminProspectDeleteHandler),
                   Route('/prospects/<prospect_id>', prospects_handler.AdminProspectDetailsHandler),
            
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