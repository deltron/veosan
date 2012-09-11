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
        fr_index_page = en_index_page.click(linkid='lang-change-link')
        fr_index_page.mustcontain('Pour les professionnels de la santé')
        
    def test_french_index(self):
        fr_index_page = self.testapp.get('/fr')
        fr_index_page.mustcontain('Pour les professionnels de la santé')
        fr_index_page.mustcontain('English')
        en_index_page = fr_index_page.click(linkid='lang-change-link')
        en_index_page.mustcontain('For Health Care Professionals')
        
    def test_tour_page(self):
        # Francais
        fr_tour_page = self.testapp.get('/fr/tour')
        fr_tour_page.mustcontain('Aidez vos', 'patients', 'à vous trouver')
        # switch to English
        en_tour_page = fr_tour_page.click(linkid='lang-change-link')
        en_tour_page.mustcontain('Help', 'patients', 'find you')
        # english
        en_tour_page = self.testapp.get('/en/tour')
        en_tour_page.mustcontain('Help', 'patients', 'find you')
        # switch to French
        fr_tour_page = en_tour_page.click(linkid='lang-change-link')
        fr_tour_page.mustcontain('Aidez vos', 'patients', 'à vous trouver')
        
