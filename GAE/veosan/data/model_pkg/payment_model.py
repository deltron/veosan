from google.appengine.ext import ndb


class PaypalResponse(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    
    provider = ndb.KeyProperty(kind='Provider')
    
    # PDT or IPN
    message_type = ndb.StringProperty()
    raw_pdt_message = ndb.TextProperty()
    raw_ipn_message = ndb.JsonProperty()

    # Parsed PayPal Variables
    
    #payer_id=XXND8ZRLPHLGA
    payer_id = ndb.StringProperty()
    
    #txn_id=5TR15292NL030901D
    txn_id = ndb.StringProperty()
    
    #custom=ag5zfnZlb3Nhbi1zdGFnZXIPCxIIUHJvdmlkZXIYjicM
    custom = ndb.StringProperty()
    
    #mc_gross=9.99
    #settle_amount=8.13
    #payment_date=08%3A29%3A11+Sep+18%2C+2012+PDT
    #payment_status=Completed
    #charset=windows-1252
    #first_name=David
    #receipt_reference_number=
    #mc_fee=0.69
    #exchange_rate=0.874542
    #subscr_id=I-1WYVR40D1L5D
    #settle_currency=USD
    #payer_status=verified
    #business=pp_san_1347903569_biz%40veosan.com
    #payer_email=pp_san_1347906872_per%40veosan.com
    #payment_type=instant
    #last_name=Leblanc
    #receiver_email=pp_san_1347903569_biz%40veosan.com
    #receiver_id=Q2CLDAYV6YQH4
    #pos_transaction_type=
    #txn_type=subscr_payment
    #item_name=Veosan+Presence
    #mc_currency=CAD
    #residence_country=CA
    #transaction_subject=Veosan+Presence