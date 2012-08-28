# -*- coding: utf-8 -*-

from handler.base import BaseHandler
from data import db
import logging
from google.appengine.api import logservice
import time
import mail
import datetime

class MailErrorHandler(BaseHandler):
    def get(self):
        # offset doesn't work. I give up.
        
        site_counter = db.get_site_counter()
        log_email_last_offset = site_counter.log_email_last_offset
        end_time = time.time()
        
        last_offset = None
        message = ""
        
        for req_log in logservice.fetch(end_time=end_time, offset=log_email_last_offset,
                                    #minimum_log_level=logservice.LOG_LEVEL_WARNING,
                                    include_app_logs=True):
            
            message += datetime.datetime.fromtimestamp(int(req_log.end_time)).strftime('%Y-%m-%d %H:%M:%S')
            message += "\n"
            message += req_log.ip
            message += "\n"
            if req_log.referrer:
                message += req_log.referrer
                message += "\n"
            
            message += req_log.resource
            message += "\n"

            message += "\n APP MESSAGES \n"
            for app_log in req_log.app_logs:
                if app_log.level >= 3:
                    message += "Log Level: " + str(app_log.level) + "\n"           
                    message += app_log.message 
                    message += "\n"

            message += "\n\n -------------------------------- \n\n"
            last_offset = req_log.offset

        if last_offset:
            site_counter.log_email_last_offset = last_offset
            site_counter.put()
        
        logging.info("-------------------------")
        logging.info(message)
        
        #mail.email_error_log_report(message)
        
