# -*- coding: utf-8 -*-

from handler.base import BaseHandler
from forms.contact import ContactForm
import mail

class ContactHandler(BaseHandler):
    def get(self):
        self.render_template("contact.html", form=ContactForm(self.request.GET))

    def post(self):
        contact_form = ContactForm(self.request.POST)
        if contact_form.validate():
            try: 
                mail.email_contact_form(self.jinja2, contact_form.from_email.data, contact_form.subject.data, contact_form.message_body.data)
                self.render_template('contact.html', form=contact_form, success_message=_(u"Your comments were sent succesfully. Thanks for your feedback, we will contact you shortly to follow up. Have a great day!"))
            except Exception as e:
                self.render_template('contact.html', error_message=_(u"Sorry, there was an error sending your comments. Please call 555-123-1212 to talk to someone."))
        else:
            self.render_template('contact.html', form=contact_form)