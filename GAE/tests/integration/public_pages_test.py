# -*- coding: utf-8 -*-

from base import BaseTest
import unittest
from data import db

class ProviderSocialTest(BaseTest):
    
    def test_default_language(self):
        index_page = self.testapp.get('/')
        index_page.mustcontain(u'Pour les professionnels de la santé')
        index_page.mustcontain('Blogue')
        
        
    def test_english_index(self):
        en_index_page = self.testapp.get('/en')
        en_index_page.mustcontain('For Health Care Professionals')
        en_index_page.mustcontain('Français')
        
    def test_french_index(self):
        en_index_page = self.testapp.get('/fr')
        en_index_page.mustcontain('Pour les professionnels de la santé')
        en_index_page.mustcontain('English')