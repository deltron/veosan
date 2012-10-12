
from forms.user import PasswordForm
from webapp2_extras import security 
from handler import auth
from data import db
import logging
import urlparse
import mail
from handler.user_pkg.user_base_handler import UserBaseHandler



class PasswordHandler(UserBaseHandler):        
    def post(self, token=None):
        password_form = PasswordForm().get_form(self.request.POST)
        
        user = self.validate_token(token)
        
        if user and password_form.validate():        
            # get password from request
            password = self.request.get('password')
                
            # hash password (same as passing password_raw to user_create)
            password_hash = security.generate_password_hash(password, length=12)    
            user.password = password_hash
            user.put()
            
            # login with new password
            self.login_user(user.get_email(), password)
               
            # clear the password reset key to prevent further shenanigans
            self.delete_token(token, 'reset')
            
            if auth.PROVIDER_ROLE in user.roles:
                provider = db.get_provider_from_user(user)
                self.redirect('/provider/message/reset/' + provider.vanity_url)
                self.log_event(user, "Password reset for user")
            
            elif auth.PATIENT_ROLE in user.roles:
                patient = db.get_patient_from_user(user)
                self.redirect('/patient/bookings/' + patient.key.urlsafe())

        # password form was not validate, re-render and try again!
        else:
            self.render_template('user/password.html', form=password_form, token=token)

        


class ResetPasswordHandler(UserBaseHandler):
    def get(self, token=None):
        ''' Someone coming back with a password reset token '''
        #parse URL to get password reset key
        if token:
            user = self.validate_token(token)
            if user:            
                # got a good user for that password reset token, show the password form
                password_form = PasswordForm().get_form()                
                self.render_template('user/password.html', form=password_form, token=token)
            else:
                # no user found for password reset key, send them to the login page
                error_message = _("Sorry, your link is expired, please try again.")
                logging.info("(ProviderResetPasswordHandler.get) can't find anyone for that password reset link: %s" % token)
                self.render_login(error_message=error_message)
        else:
            logging.info('(ProviderResetPasswordHandler.get) No password reset key in request')
        
        
    def post(self):
        ''' Someone forgot their password, generate a token and send email '''
        email = self.request.get('email')

        logging.info("(ProviderResetPasswordHandler.post) got password reset request for email: %s" % email)
        if email:            
            user = db.get_user_from_email(email)
        
            if user:
                self.create_token(user, 'reset')
                
                # resetpassword url
                url_obj = urlparse.urlparse(self.request.url)
                passwordreset_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, '/user/resetpassword/' + user.resetpassword_token, '', '', ''))
                logging.info('(ProviderResetPasswordHandler.post) password reset URL:' + passwordreset_url)
            
                # send email
                mail.email_user_password_reset(self.jinja2, user, passwordreset_url)
            
                # render the login page with success message
                success_message = _('Password reset instructions have been sent to your address on file.')
                logging.info("(ProviderResetPasswordHandler.post) " + success_message)
                self.render_login(success_message=success_message)
            else:
                logging.info("(ProviderResetPasswordHandler.post) Can't reset password, no provider exists for email: %s" % email)
                self.render_login()
