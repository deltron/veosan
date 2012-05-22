# -*- coding: utf-8 -*-
from base import BaseHandler
# webapp2 auth service
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
# google user service
from google.appengine.api import users
# clik
from forms import LoginForm

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
            username = self.request.POST.get('username')
            password = self.request.POST.get('password')
            remember_me = True if self.request.POST.get('remember_me') == 'on' else False
            # Username and password check
            try:
                self.auth.get_user_by_password(username, password, remember=remember_me)
                self.redirect('/admin')
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



