from webapp2_extras.routes import PathPrefixRoute
from webapp2 import Route
from handler import admin, provider_admin
from handler.admin_pkg import data_handler, admin_bookings_handler,\
    prospects_handler, campaign_handler, domain_handler


def get_routes():
    return [PathPrefixRoute('/admin', [
                   Route('/bookings', admin_bookings_handler.AdminBookingsHandler),
                   Route('/booking/<operation>/<booking_key>', admin_bookings_handler.AdminBookingDetailHandler),
                   Route('/providers', admin.AdminProvidersHandler),
                   Route('/patients', admin.AdminPatientsHandler),
                   Route('/invites', admin.AdminInvitesHandler),
                   Route('/dashboard', admin.AdminDashboardHandler),
                   Route('/domain', domain_handler.DomainSetupHandler),
                   Route('/domain/<domain>', domain_handler.DomainSetupHandler),
                   Route('/domain/<domain>/setup', domain_handler.DomainSetupHandler),
                   Route('/data', data_handler.AdminDataHandler),
                   Route('/data/stage', data_handler.AdminStageDataHandler),
                   Route('/data/delete', data_handler.AdminDeleteDataHandler),
            
                   Route('/site_config/<feature>', admin.AdminSiteConfigHandler),
                   
                   # prospects
                   Route('/prospects', prospects_handler.AdminProspectsHandler),
                   Route('/prospects/search', prospects_handler.AdminProspectsHandler, handler_method='search'),
                   Route('/prospects/delete/<prospect_id>', prospects_handler.AdminProspectDeleteHandler),
                   Route('/prospects/<prospect_id>', prospects_handler.AdminProspectDetailsHandler),
                   Route('/prospects/<prospect_id>/notes/<operation>', prospects_handler.AdminProspectNotesHandler),
                   Route('/prospects/<prospect_id>/notes/<operation>/<key>', prospects_handler.AdminProspectNotesHandler),
                   Route('/prospects/<prospect_id>/tags', prospects_handler.AdminProspectTagsHandler),
                   Route('/prospects/<prospect_id>/employment', prospects_handler.AdminProspectEmploymentTagsHandler),
                   Route('/prospects/<prospect_id>/campaign', prospects_handler.AdminProspectAddToCampaignHandler),
                   

                   # campaigns
                   Route('/campaigns', campaign_handler.AdminCampaignsHandler),
                   Route('/campaign/delete/<campaign_key>', campaign_handler.AdminCampaignDeleteHandler),
                   Route('/campaign/<campaign_key>', campaign_handler.AdminCampaignDetailsHandler),
                   Route('/campaign/<campaign_key>/prospects', campaign_handler.AdminCampaignDetailsHandler, methods=['GET'], handler_method='edit_prospects_get'),
                   Route('/campaign/<campaign_key>/prospects', campaign_handler.AdminCampaignDetailsHandler, methods=['POST'], handler_method='edit_prospects_post'),
                   Route('/campaign/<campaign_key>/emails', campaign_handler.AdminCampaignDetailsHandler, handler_method='generate_emails_get'),
                   Route('/campaign/<campaign_key>/email/<prospect_id>', campaign_handler.AdminCampaignDetailsHandler, handler_method='display_single_email_get'),
                   Route('/campaign/<campaign_key>/sent/<prospect_id>', campaign_handler.AdminCampaignDetailsHandler, handler_method='mark_as_sent_post'),
                   
                   PathPrefixRoute('/provider', [                                            
                       # provider admin
                       Route('/admin/<vanity_url>', provider_admin.ProviderAdministrationHandler),
                    
                       # custom domain
                       Route('/vanitydomain/<vanity_url>', provider_admin.ProviderDomainHandler),

                       # custom domain
                       Route('/forcefriends/<vanity_url>', provider_admin.ProviderForceFriendsHandler),
                                        
                       # change password
                       Route('/changepassword/<vanity_url>', provider_admin.ProviderChangePasswordHandler),
                        
                       # generate claim
                       Route('/generateclaim/<vanity_url>', provider_admin.ProviderGenerateClaimHandler),

                       # set domain
                       Route('/canonicaldomain/<vanity_url>', provider_admin.ProviderDomainSetupHandler),

                       # logs
                       Route('/logs/<vanity_url>', provider_admin.ProviderEventLogHandler),
            
                       Route('/feature/<feature_switch>/<vanity_url>', provider_admin.ProviderFeaturesHandler),
                    ]),
               ]),
            ]