# -*- coding: utf-8 -*-

from handler.base import BaseHandler
from forms.contact import ContactForm
import mail
import util
import logging
from webapp2_extras.i18n import gettext as _
from data import db

class ContactHandler(BaseHandler):
    def get(self):
        contact_form = ContactForm().get_form()
        
        self.render_template("contact.html", form=contact_form)

    def post(self):
        contact_form = ContactForm().get_form(self.request.POST)
        if contact_form.validate():
            try: 
                mail.email_contact_form(self.jinja2, contact_form.from_email.data, contact_form.subject.data, contact_form.message_body.data)
                self.render_template('contact.html', form=contact_form, success_message=_(u"Your comments were sent succesfully. Thanks for your feedback, we will contact you shortly to follow up. Have a great day!"))
            except Exception as e:
                self.render_template('contact.html', error_message=_(u"Sorry, there was an error sending your comments. Please call (514) 998-1286 to talk with someone."))
        else:
            self.render_template('contact.html', form=contact_form)
            
class TeaserHandler(BaseHandler):
    def get_form(self, request=None):
        if request:
            signup_form = TeaserForm(request)
        else:
            signup_form = TeaserForm()
            
        return signup_form

    def get(self):
        self.redirect("/")
    
    def post(self):        
        signup_form = self.get_form(self.request.POST)

        if signup_form.validate():
            email = self.request.get('from_email')
            postalcode = self.request.get('postal_code')
            role = self.request.get('role')
            lang = self.get_language()

            message = "Received sign-up request from \n\n \
                          email: %s \n \
                          postal_code: %s \n \
                          role: %s \n \
                          language: %s \n \n\n\n" % (email, postalcode, role, lang)

            logging.info(message)

            from_email = mail.VEOSAN_SUPPORT_ADDRESS
            subject = "Request for signup : %s" % email

            mail.email_contact_form(self.jinja2, from_email, subject, message)

            success_message = _('Thanks for your interest. We will be in touch soon!')
            self.render_template('index.html', signup_form=self.get_form(), success_message=success_message)
        else:
            self.render_template('index.html', signup_form=signup_form)


class SignupHandler(BaseHandler):
    def get(self):
        new_provider_form = NewProviderForm().get_form()
        self.render_template('user/signup.html', new_provider_form=new_provider_form)

    def post(self):
        new_provider_form = NewProviderForm().get_form(self.request.POST)
        
        if new_provider_form.validate():
            email = self.request.get('email')
            vanity_url = self.request.get('vanity_url')

            # force the inputs to lowercase
            email = email.lower()
            vanity_url = vanity_url.lower()

            provider_key = db.init_provider(email, vanity_url)
            logging.info('(SignupHandler.post) Initialized new provider vanity_url=%s email=%s' % (vanity_url, email))
            provider = provider_key.get()
            
            # now create an empty user for the provider
            user = self.create_empty_user_for_provider(provider)
            
            # create a signup token for new user
            token = self.create_signup_token(user)

            # send them over to the password page with this token
            self.redirect('/user/password/' + user.signup_token)
        else:
            self.render_template('user/signup.html', new_provider_form=new_provider_form)
