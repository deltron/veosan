# -*- coding: utf-8 -*-

import logging
from  handler.base import BaseHandler
from forms import ContactForm


class StaticHandler(BaseHandler):
    def get(self):
        template = "static/" + self.request.route.name + ".html"
        self.render_template(template)
        

class ContactHandler(BaseHandler):
    def get(self):
        self.render_template("contact.html", form=ContactForm(self.request.GET), sent=False)

    def post(self):
        contact_form = ContactForm(self.request.POST)
        if contact_form.validate():
            from_email = contact_form.email.data
            subject = contact_form.subject.data
            message = contact_form.message.data
            
            # send email
            # show confirmation page
            
            logging.info('Feedback from %s | subject: %s\n\nMESSAGE\n=========\n%s' % (from_email, subject, message))
            
            self.render_template('contact.html', form=contact_form, sent=True)
        else:
            self.render_template('contact.html', form=contact_form, sent=False)

