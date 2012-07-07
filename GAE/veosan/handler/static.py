# -*- coding: utf-8 -*-

from  handler.base import BaseHandler

class StaticHandler(BaseHandler):
    def get(self):
        template = "static/" + self.request.route.name + ".html"
        self.render_template(template)
        