

import urlparse
import logging
from util import LANGUAGES


def get_language_from_url(url):
    '''
        returns the language code at the start of the url path ie: en or fr
        return None if URL does not start with a language code.
    '''
    url_obj = urlparse.urlparse(url)
    path = url_obj.path
    if path:
        path_split = path.split('/')
        lang = path_split[1]
    if lang in LANGUAGES:
        logging.info('Setting lang from url %s' % lang)
        return lang
    else:
        return None
    
    
def is_url_index(url):
    url_obj = urlparse.urlparse(url)
    path = url_obj.path
    return path == '/'


def is_url_translatable(url):
    start_with_slash_lang = get_language_from_url(url) != None
    is_index = is_url_index(url)
    return start_with_slash_lang or is_index


def get_url_post_language(url):
    '''
        return everything after /en or /fr
    '''
    url_obj = urlparse.urlparse(url)
    path = url_obj.path
    return path[3:]