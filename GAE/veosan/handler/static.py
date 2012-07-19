# -*- coding: utf-8 -*-

from handler.base import BaseHandler
from data import db

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


class SitemapHandler(BaseHandler):
    def get(self):
        vanity_url_list = db.get_all_vanity_urls()
        self.render_template("sitemap.xml", vanity_url_list=vanity_url_list)

class RobotsHandler(BaseHandler):
    def get(self):
        self.render_template("robots.txt")


class SalesHandler(BaseHandler):
    def get(self, page=None):
        pages = {
                  'who' : 'sales/who.html',
                  'price' : 'sales/price.html',
                 }
        if page:
            self.render_template(pages[page])
        else:
            self.render_template("sales/index.html")


class DomainDispatcher(BaseHandler):
    def get(self, domain=None):
        provider = db.get_provider_from_domain(domain)
        self.redirect('http://www.veosan.com/' + provider.vanity_url)

