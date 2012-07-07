# -*- coding: utf-8 -*-
import unittest
from base import BaseTest

class ContactTest(BaseTest):
        def test_feedback_email(self):
            ''' Send feedback and check it gets received '''

            response = self.testapp.get('/contact')
            
            contact_form = response.forms[0] # contact form
            contact_form['from_email'] = 'foo_tester@bar.com' 
            contact_form['subject'] = 'Quick brown foxes'
            contact_form['message_body'] = 'I need to see someone about a horse.'
            
            response = contact_form.submit()
            
            # check the user received a success message
            response.mustcontain("Vos commentaires ont été envoyés avec succès.")
            
            
            # check we got the email            
            messages = self.mail_stub.get_sent_messages(to='support@veosan.com')
            self.assertEqual(1, len(messages))
            m = messages[0]
            
            
            self.assertEqual(m.subject, 'Quick brown foxes')
            self.assertEqual(m.sender, 'foo_tester@bar.com')
            self.assertEqual(m.body.payload, 'I need to see someone about a horse.')


        def test_feedback_email_invalid_from_address(self):
            ''' Send feedback with an invalid from address '''

            response = self.testapp.get('/contact')
            
            contact_form = response.forms[0] # contact form
            contact_form['from_email'] = 'bobsnob' 
            contact_form['subject'] = 'Quick brown foxes'
            contact_form['message_body'] = 'I need to see someone about a horse.'
            
            response = contact_form.submit()
            
            # check the user received the proper error message            
            response.mustcontain("Addresse courriel invalide.")
            
 
        def test_feedback_email_no_subject(self):
            ''' Send feedback and check it gets received '''

            response = self.testapp.get('/contact')
            
            contact_form = response.forms[0] # contact form
            contact_form['from_email'] = 'bobsnob' 
            contact_form['subject'] = ''
            contact_form['message_body'] = 'I need to see someone about a horse.'
            
            response = contact_form.submit()
            
            # check the user received the proper error message            
            response.mustcontain("Addresse courriel invalide.")
                    


if __name__ == "__main__":
    unittest.main()
    
    
