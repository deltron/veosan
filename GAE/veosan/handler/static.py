# -*- coding: utf-8 -*-

from  handler.base import BaseHandler

class StaticHandler(BaseHandler):
    def get(self):
        template = "static/" + self.request.route.name + ".html"
        self.render_template(template)
        
        
class WarmupHandler(BaseHandler):
    def get(self):
        ''' Handle a warmup request from GAE.
        This page is hit every time a new instance is loaded. '''
        
        # render the home page, hopefully preloads everything we need
        self.redirect("/")
        