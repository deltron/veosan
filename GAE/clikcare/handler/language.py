
#clik
from base import BaseHandler

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
        url = self.request.headers.get('Referer', '/')
        self.redirect(url)