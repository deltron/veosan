from handler.base import BaseHandler
from data import db

class ProspectHandler(BaseHandler):
    def get(self, prospect_id = None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        
        if prospect:
            if "X-AppEngine-Country" in self.request.headers:
                prospect.gae_country = self.request.headers["X-AppEngine-Country"]
    
            if "X-AppEngine-Region" in self.request.headers:
                prospect.gae_region = self.request.headers["X-AppEngine-Region"]
    
            if "X-AppEngine-City" in self.request.headers:
                prospect.gae_city = self.request.headers["X-AppEngine-City"]
    
            if "X-AppEngine-CityLatLong" in self.request.headers:
                prospect.gae_city_lat_long = self.request.headers["X-AppEngine-CityLatLong"]

            prospect.landing_hits += 1
            prospect.put()
            self.session['prospect_id'] = prospect.prospect_id
            self.redirect(prospect.prospect_landing)
        else:
            self.redirect("/")
        
