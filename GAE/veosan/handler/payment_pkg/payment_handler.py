from handler.base import BaseHandler
import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from handler.auth import provider_required
import logging
import re
from urllib import unquote_plus

PP_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr" 
PP_EMAIL = "pp_san_1347903569_biz@veosan.com" 
PP_PDT_TOKEN = "BQcv8Sc-hiDvMwKPXhaVodW090MojUfgClMdWRWHO51AVvRIMV3QOqiE3Oi"

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
            
            try:
                # Do a post back to validate
                # the transaction data
                status = urlfetch.fetch(url=PP_URL, method=urlfetch.POST, payload=encode_param).content
            except:
                self.response.out.write("POST Failed") 
                        
            if status == "VERIFIED":
                # upgrade the account...woohoo!
                provider_urlsafe_key = param['custom']
                user_key = ndb.Key(urlsafe=provider_urlsafe_key)
                
            else:
                self.response.out.write('error') 
        
class ProviderUpgradeSuccessHandler(BaseHandler):
    def get(self):
        param = {} 
        transaction_token = self.request.get('tx')
            
        # POST to PayPal to get the details
        param['tx'] = transaction_token
        param['at'] = PP_PDT_TOKEN
        param['cmd'] = '_notify-synch'
        encode_param = urllib.urlencode(param) 
         
        try:
            # Do a post back to validate
            # the transaction data
            status = urlfetch.fetch(url=PP_URL, method=urlfetch.POST, payload=encode_param).content
        except:
            self.response.out.write("POST Failed") 
            
        # Check for SUCCESS at the start of the response
        if re.search("^SUCCESS", status):
            response_list = status.split('\n')
            response_dict = {}
            for i, line in enumerate(response_list):
                unquoted_line = unquote_plus(line).strip()        
                if i == 0:
                    self.st = unquoted_line
                    if self.st == "SUCCESS":
                        result = True
                else:
                    if self.st != "SUCCESS":
                        self.set_flag(line)
                        break
                    try:                        
                        if not unquoted_line.startswith(' -'):
                            k, v = unquoted_line.split('=')                        
                            response_dict[k.strip()] = v.strip()
                    except ValueError, e:
                        pass
            
            provider = None
            if response_dict.has_key('custom'):
                provider_urlsafe_key = response_dict['custom']
                provider_key = ndb.Key(urlsafe=provider_urlsafe_key)
                provider = provider_key.get()
            
            # switch on account options
            
            self.render_template("provider/upgrade_success.html", provider=provider, status=status )#provider=provider)
            
        else:
            self.response.out.write("Failed")
