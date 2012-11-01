# -*- coding: utf-8 -*-
import unittest
from base import BaseTest

class SitemapTest(BaseTest):
    def test_get_robots(self):
        response = self.testapp.get('/robots.txt')
        
        # no domain, disallow crawl
        response.mustcontain('Disallow: /')

    def test_get_sitemap(self):
        self.create_complete_provider_profile()
        response = self.testapp.get('/sitemap.xml')
        response.mustcontain('http://www.localhost/' + self._TEST_PROVIDER_VANITY_URL)
        

if __name__ == "__main__":
    unittest.main()
    
    
