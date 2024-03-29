from base import BaseHandler
import logging

class LanguageHandler(BaseHandler):
    '''
        Handler to change language
    '''
    def get(self, lang = 'fr', hide_side = None):
        '''
            Changes language and redirect to current page
        '''
        self.set_language(lang)
        
        # save language into user
        user = self.get_current_user()
        if user:
            user.language = lang
            user.put()
        
        # hide sidebar
        if hide_side == 'hide_side':
            self.session['hide-lang'] = True
            self.redirect('/' + lang)
        
        else:
            # redirect to referrer or /
            referer = self.request.headers.get('Referer')
            logging.info('(LanguageHandler.get) Changing language to %s: referer is %s' % (lang, referer))
            
            referer_url = self.request.headers.get('Referer', '/')
            redirect_url = referer_url
                
            self.redirect(redirect_url)