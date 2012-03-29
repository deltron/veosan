'''
    base handler
'''

import webapp2
from webapp2_extras import jinja2
import gettext

t = gettext.translation('clikcare', 'locale', languages=['fr'], fallback='en')
t.install()


class BaseHandler(webapp2.RequestHandler):        
    @webapp2.cached_property
    def jinja2(self):
        j = jinja2.get_jinja2(app=self.app)
        j.environment.install_gettext_translations(t)
        return j

    def render_template(self, filename, **template_args):
        self.response.write(self.jinja2.render_template(filename, **template_args))