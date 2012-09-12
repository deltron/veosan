# -*- coding: utf-8 -*-

from handler.base import BaseHandler
from data import db
import logging
import urlparse
import util

class StaticHandler(BaseHandler):
    def render_static(self, name):
        # set language
        self.set_language_from_url()
        # render
        template = "static/" + name + ".html"
        self.render_template(template)

    def get_about(self):
        self.render_static('about')

    def get_careers(self):
        self.render_static('careers')

    def get_terms(self):
        self.render_static('terms')

    def get_privacy(self):
        self.render_static('privacy')

    def get_tour(self):
        self.render_static('tour')

        
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
                  'corporate' : 'sales/corporate.html',
                  'institution' : 'sales/institution.html',
                  'competition' : 'sales/competition.html',
                  'community' : 'sales/community.html',
                 }
        if page:
            self.render_template(pages[page])
        else:
            self.render_template("sales/index.html")


class DomainDispatcher(BaseHandler):
    def get(self, domain=None):
        logging.info("(DomainDispatcher) activated with domain %s " % domain)
            
        provider = db.get_provider_from_domain(domain)
        if provider:
            logging.info("(DomainDispatcher) Received domain %s and matched to provider vanity_url %s " % (domain, provider.vanity_url))
            redirect_url = 'http://www.veosan.com/%s' % (str(provider.vanity_url))
            self.redirect(redirect_url, permanent=True)
        else:
            self.redirect('http://www.veosan.com/')

    
class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('index.html')
        
    def get_en(self):
        self.set_language('en')
        self.render_template('index.html')

    def get_fr(self):
        self.set_language('fr')
        self.render_template('index.html')



class HideSideHandler(BaseHandler):
    def get(self, what = None):
        if what == 'lang':
            self.session['hide-lang'] = True
            logging.info("Hide lang sidebar")

        if what == 'patient':
            self.session['hide-patient'] = True
            logging.info("Hide patient sidebar")

        self.render_template("empty.html")


class BlogHandler(BaseHandler):
    def get(self, what = None):
        site_counter = db.get_site_counter()
        site_counter.blog_clicks += 1
        
        # figure out the language
        url_obj = urlparse.urlparse(self.request.url)
        path = url_obj.path
        if path:
            path_split = path.split('/')
            lang = path_split[1]
        if lang in util.LANGUAGES:
            logging.info('Setting lang from url %s' % lang)
            self.set_language(lang)

        
        if self.get_language() == 'fr':
            site_counter.blog_clicks_fr += 1
            self.redirect("http://blogue.veosan.com")
        else:
            site_counter.blog_clicks_en += 1
            self.redirect("http://blog.veosan.com")

        site_counter.put_async()

