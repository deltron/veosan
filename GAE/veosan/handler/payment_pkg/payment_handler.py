from handler.base import BaseHandler
import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

PP_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr" 
PP_EMAIL = "pp_san_1347646549_biz@veosan.com" 

class PayPalIPNHandler(BaseHandler):
    def get(self):
        self.do_request()
        
    def post(self):
        self.do_request()
    
    def do_request(self):
        # paypal will hit this with an incoming message
        param = None 
        if self.request.get('payment_status') == 'Completed': 
            if self.request.POST: 
                param = self.request.POST.copy() 
            if self.request.GET: 
                param = self.request.GET.copy() 
        
        # send it back to paypal for verification
        if param: 
            param['cmd'] = '_notify-validate' 
            encode_param = urllib.urlencode(param) 
            status = urlfetch.fetch(url=PP_URL, method=urlfetch.POST, payload=encode_param).content 
                        
            if status == "VERIFIED":
                # upgrade the account...woohoo!
                provider_urlsafe_key = param['custom']
                user_key = ndb.Key(urlsafe=provider_urlsafe_key)
                
            else:
                self.response.out.write('error') 
        

