# -*- coding: utf-8 -*-
import logging
from base import BaseHandler
# webapp2 auth service
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
# google user service
from google.appengine.api import users
# clik
from forms.base import LoginForm
import data
from data.model import Provider, Patient


# Roles
PROVIDER_ROLE = 'Provider'
PATIENT_ROLE = 'Patient'


def user_required(handler):
    '''
        Decorator
        Checks session for authenticated user OR google admin user
    '''
    def check_login(self, *args, **kwargs):
        if self.auth.get_user_by_session() or users.is_current_user_admin():
            handler(self, *args, **kwargs)
            # no return, we use jinja templates
        else:
            self.redirect('/login', abort=True)
            
    # decorator returns check_login function    
    return check_login


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
                auth_user = self.auth.get_user_by_password(email, password, remember=remember_me)
                user = self.get_current_user()
                logging.info('Login succesful for %s' % user)
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



