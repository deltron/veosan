import logging
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import urllib

class BlobServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    ''' Serve a blob with key. call URL as
            /serve/xxx   where xxx = blob store key
    '''
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        logging.info("Serving blob image: %s" % resource)
        
        self.send_blob(resource)