from handler.admin import AdminBaseHandler
import util
import logging
from google.appengine.ext import ndb


class AdminDataHandler(AdminBaseHandler):
    ''' Administer Providers '''

    def get(self):        
        self.render_data()


class AdminStageDataHandler(AdminBaseHandler):
    ''' Administer Providers '''

    def post(self):
        if util.is_dev_server(self.request):
            logging.info('*** Generating test data for providers')
            from data import test_data
            test_data.create_test_providers()
            self.render_data(success_message="Generated provider data successfully")

        else:
            logging.info('*** Someone tried to Generating test data for providers on a production server. WTF!?')
            self.render_data(error_message="Production server, cannot generate test provider data")

class AdminDeleteDataHandler(AdminBaseHandler):
    ''' Delete all data from database '''

    def post(self):
        logging.info('self.request.host %s' % self.request.host)
        
        if util.is_dev_server(self.request):
            confirm_text = self.request.get('confirm_text')
            if confirm_text == 'delete':
                all_entities = ndb.Query().fetch(keys_only=True)
                logging.info('*** DELETE ALL ENTITIES: %s' % all_entities)
                for e in all_entities: 
                    e.delete()
                self.render_data(success_message="Everything deleted")
            else:
                self.render_data(error_message="Missing confirmation code")

        else:
            logging.info('*** Someone tried to delete everything from a production server. WTF!?')
            self.render_data(error_message="Production server, cannot delete")

