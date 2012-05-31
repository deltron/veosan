# -*- coding: utf-8 -*-
import logging
from base import BaseHandler
# webapp2 auth service
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
# google user service
from google.appengine.api import users
from webapp2_extras.appengine.users import admin_required as google_admin_required
# clik
from forms.login import LoginForm
import data
from data.model import Provider


# Roles
PROVIDER_ROLE = 'Provider'
PATIENT_ROLE = 'Patient'

# admin_required uses the google user system
admin_required = google_admin_required

def provider_required(handler_method):
    '''
        Decorator: Checks session for authenticated provider (or google admin)
    '''
    
    def check_provider_key(self):
        user = self.get_current_user()
        if user:
            provider = data.db.get_first_provider_profile(user)
            if provider:
                return provider.key.urlsafe() == self.request.get('key')   
            else:
                logging.info('provider_required failed. Provider key does not match request key %s <> $s' % (provider.key.urlsafe(), self.request.get('key')))
        else:
            logging.info('provider_required failed: User is None')
        return False

    def check_provider_login(self, *args, **kwargs):
        # admin
        if users.is_current_user_admin():
            handler_method(self, *args, **kwargs)
        # provider logged in with key matching request key
        elif check_provider_key(self):
            handler_method(self, *args, **kwargs)
        else:
            self.redirect('/login', abort=True)
            
    # decorator returns check_login function    
    return check_provider_login


class LoginHandler(BaseHandler):
    '''
        GET shows login page
        POST checks username, password and logs in user
    '''
    def get(self):
        login_form = LoginForm()
        self.render_template('login.html', form=login_form)

    def post(self):
        login_form = LoginForm(self.request.POST)
        if login_form.validate():
            email = self.request.POST.get('email')
            password = self.request.POST.get('password')
            remember_me = True if self.request.POST.get('remember_me') == 'on' else False
            logging.info('Trying to login email:%s' % email)
            # Username and password check
            try:
                user = self.login_user(email, password, remember_me)
                # login was succesful, User is in the session
                profiles = data.db.get_user_profiles(user)
                logging.info('profiles: %s' % profiles)
                # redirect to the first profile type
                if len(profiles) > 0:
                    profile = profiles[0]
                    if isinstance(profile, Provider):
                        redirect_url = profile.get_edit_link('bookings')
                        self.redirect(redirect_url)
                    else:
                        self.redirect('/')
                else:
                    logging.error('User %s logged in without roles')
                    error_message = 'Your profile is not activated. Please contact us.'
                    self.render_template('login.html', form=login_form, error_message=error_message)
                
            except (InvalidAuthIdError, InvalidPasswordError), e:
                # throws InvalidAuthIdError if user is not found, throws InvalidPasswordError if provided password doesn't match with specified user
                error_message = 'Login failed. Try again.'
                self.render_template('login.html', form=login_form, error_message=error_message)
        else:
            # form validation error
            self.render_template('login.html', form=login_form)



class LogoutHandler(BaseHandler):
    '''
        Unset user session and redirect to index
    '''
    def get(self):
        self.auth.unset_session()
        self.redirect('/')



