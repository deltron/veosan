# -*- coding: utf-8 -*-

from handler.base import BaseHandler
from data import db
import logging
import urlparse
import util
from data.model_pkg.provider_model import Provider
import data
import json

class StaticHandler(BaseHandler):
    def render_static(self, name, prospect_id = None):
        # set language
        self.set_language_from_url()
        
        # set prospect
        if prospect_id:
            self.log_prospect(prospect_id)
        
        # render
        template = "static/" + name + ".html"
        self.render_template(template)

    def get_about(self, prospect_id = None):
        self.render_static('about', prospect_id)

    def get_careers(self, prospect_id = None):
        self.render_static('careers', prospect_id)

    def get_terms(self, prospect_id = None):
        self.render_static('terms', prospect_id)

    def get_privacy(self, prospect_id = None):
        self.render_static('privacy', prospect_id)

    def get_tour(self, prospect_id = None):
        self.render_static('tour', prospect_id)

    def get_browser_upgrade(self, prospect_id = None):
        self.render_static('internet_explorer', prospect_id)

        
class WarmupHandler(BaseHandler):
    def get(self):
        ''' Handle a warmup request from GAE.
        This page is hit every time a new instance is loaded. '''
        
        # render the home page, hopefully preloads everything we need
        self.redirect("/")


class SitemapHandler(BaseHandler):
    def get(self):
        #vanity_url_list = db.get_all_vanity_urls()
        
        domain_without_ports = self.request.host.split(":")[0]
        domain_without_www = domain_without_ports.replace("www.", "")
        
        categories = []
        
        domain_setup = data.db.get_domain_setup(domain_without_www)
        if domain_setup and domain_setup.categories_json:
            categories_json = domain_setup.categories_json
            categories_from_json = json.loads(categories_json)
            
            for (key, english_string) in categories_from_json:
                categories.append(key)
        
        vanity_url_list = []
        if categories:
            vanity_url_list = Provider.query(Provider.category.IN(categories)).fetch(projection=['vanity_url'])            
        
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
    def get_index_file(self):    
        domain_without_ports = self.request.host.split(":")[0]
        domain = domain_without_ports.replace("www.", "")
        domain_setup = db.get_domain_setup(domain)
        index_file = 'index.html'
        if domain_setup and domain_setup.index_file:
            index_file = domain_setup.index_file
            
        return index_file

    
    def get(self):        
        self.render_template(self.get_index_file())
        
    def get_en(self):
        self.set_language('en')
        self.render_template(self.get_index_file())

    def get_fr(self):
        self.set_language('fr')
        self.render_template(self.get_index_file())



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
    def get(self, what = None, prospect_id = None):
        site_counter = db.get_site_counter()
        site_counter.blog_clicks += 1
        
        language = util.DEFAULT_LANG
        
        # set prospect and redirect based on that
        if prospect_id:
            prospect = db.get_prospect_from_prospect_id(prospect_id)
            if prospect:
                self.log_prospect(prospect_id)
                language = prospect.language
            else:
                # default language to english for blog since there are more posts
                language = 'en'
            
        else:
            # figure out the language
            url_obj = urlparse.urlparse(self.request.url)
            path = url_obj.path
            if path:
                path_split = path.split('/')
                lang = path_split[1]
            if lang in util.LANGUAGES:
                logging.info('Setting lang from url %s' % lang)
                self.set_language(lang)
                
            language = self.get_language()
        
        if language == 'fr':
            site_counter.blog_clicks_fr += 1
            self.redirect("http://blogue.veosan.com")
        else:
            site_counter.blog_clicks_en += 1
            self.redirect("http://blog.veosan.com")

        site_counter.put_async()
        self.log_entry()

