from webapp2 import Route
from handler.payment_pkg import payment_handler
from webapp2_extras.routes import PathPrefixRoute


# routes for payments
def get_routes():
    return [
            
                   PathPrefixRoute('/payment', [

                       Route('/ipn', handler=payment_handler.PayPalIPNHandler),
                       Route('/success', handler=payment_handler.ProviderUpgradeSuccessHandler),
                    
                    ])
            ]
    
