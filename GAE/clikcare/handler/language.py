from base import BaseHandler
import logging

class LanguageHandler(BaseHandler):
    '''
        Handler to change language
    '''
    def get(self, lang):
        '''
            Changes language and redirect to current page
        '''
        self.set_language(lang)
        
        # redirect to referrer or /
        referer = self.request.headers.get('Referer')
        logging.info('(LanguageHandler.get) Changing language to %s: referer is %s' % (lang, referer))
        
        url = self.request.headers.get('Referer', '/')
        self.redirect(url)