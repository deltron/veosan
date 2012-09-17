from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import admin, provider_admin
from handler.admin_pkg import data_handler, admin_bookings_handler,\
    prospects_handler, campaign_handler


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
                   # prospects
                   Route('/prospects', prospects_handler.AdminProspectsHandler),
                   Route('/prospects/delete/<prospect_id>', prospects_handler.AdminProspectDeleteHandler),
                   Route('/prospects/<prospect_id>', prospects_handler.AdminProspectDetailsHandler),
                   Route('/prospects/<prospect_id>/notes/<operation>', prospects_handler.AdminProspectNotesHandler),
                   Route('/prospects/<prospect_id>/notes/<operation>/<key>', prospects_handler.AdminProspectNotesHandler),

                   # campaigns
                   Route('/campaigns', campaign_handler.AdminCampaignsHandler),
                   Route('/campaigns/delete/<campaign_key>', campaign_handler.AdminCampaignDeleteHandler),
                   Route('/campaigns/<campaign_key>', campaign_handler.AdminCampaignDetailsHandler),
                   Route('/campaign/<campaign_key>/prospects', campaign_handler.AdminCampaignDetailsHandler, handler_method='edit_prospects_post'),
                   
                   PathPrefixRoute('/provider', [
                       # provider actions
                       Route('/status', provider_admin.ProviderStatusHandler),
                                                                          
                       # provider admin
                       Route('/admin/<vanity_url>', provider_admin.ProviderAdministrationHandler),
                    
                       # custom domain
                       Route('/domain/<vanity_url>', provider_admin.ProviderDomainHandler),
                    
                       # logs
                       Route('/logs/<vanity_url>', provider_admin.ProviderEventLogHandler),
            
                       Route('/feature/<feature_switch>/<vanity_url>', provider_admin.ProviderFeaturesHandler),
                    ]),
               ]),
            ]