from handler.base import BaseHandler
from data import db


class ProspectHandler(BaseHandler):
    def get(self, prospect_id = None):
        prospect = db.get_prospect_from_prospect_id(prospect_id)
        
        if prospect:
            prospect.landing_hits += 1
            prospect.put()
            self.session['prospect_id'] = prospect.prospect_id
            self.redirect(prospect.prospect_landing)
        else:
            self.redirect("/")
        
