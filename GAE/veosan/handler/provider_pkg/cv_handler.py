#### CV Stuff
from handler.provider import ProviderBaseHandler
from forms.provider import ProviderEducationForm, ProviderExperienceForm,\
    ProviderContinuingEducationForm, ProviderOrganizationForm,\
    ProviderCertificationForm
from data.model import Education, Experience, ContinuingEducation,\
    ProfessionalOrganization, ProfessionalCertification
from handler.auth import provider_required
from data import db
from google.appengine.ext import ndb
import logging
from util import saved_message

class ProviderCVHandler(ProviderBaseHandler):
    forms = { 'education' : ProviderEducationForm,
              'experience' : ProviderExperienceForm,
              'continuing_education' : ProviderContinuingEducationForm,
              'organization' : ProviderOrganizationForm,
              'certification' : ProviderCertificationForm,
            }

    objs = { 'education' : Education,
             'experience' : Experience,
             'continuing_education' : ContinuingEducation,
             'organization' : ProfessionalOrganization,
             'certification' : ProfessionalCertification,
            }

    def generate_blank_forms(self):
        kwargs = {}
        
        # create blank forms
        for key in self.forms:
            kwargs[key + '_form'] = self.forms[key]().get_form()

        return kwargs

    @provider_required
    def get(self, vanity_url=None, section=None, operation=None, key=None):
        provider = db.get_provider_from_vanity_url(vanity_url)
        kwargs = self.generate_blank_forms()
        section_object_key = None

        if key:
            section_object_key = ndb.Key(urlsafe=key)
        
        if section_object_key:
            if operation == 'delete':
                logging.info("(ProviderEducationHandler.get) Delete section %s key=%s" % (section, key))
                            
                section_object_key.delete()
                
                # success, empty forms so you can play again            
                kwargs = self.generate_blank_forms()
            
                # log the event
                self.log_event(user=provider.user, msg="Edit CV: %s %s success" % (operation, section))

            if operation == 'edit':
                logging.info("(ProviderEducationHandler.get) Edit section %s key=%s" % (section, key))
                
                # get the object
                obj = section_object_key.get()
                
                # populate the form
                kwargs[section + "_form"] = self.forms[section]().get_form(obj=obj)
                kwargs['edit'] = section
                kwargs['edit_key'] = key


        else:
            logging.info("(ProviderEducationHandler.get) No section object found for key %s" % key)
                
        
        self.render_cv(provider, **kwargs)
    
    @provider_required
    def post(self, vanity_url=None, section=None, operation=None, key=None):

        # instantiate and fill the section form
        section_form = self.forms[section]().get_form(self.request.POST)

        provider = db.get_provider_from_vanity_url(vanity_url)

        if section_form.validate():
            # Store section
            
            if operation == 'add':
                new_section_object = self.objs[section]()
                    
                section_form.populate_obj(new_section_object)

                new_section_object.provider = provider.key
                new_section_object.put()
                
                # stored eduction
                logging.debug("(ProviderEducationHandler.post) Stored section %s key=%s" % (section, new_section_object.key))

            if operation == 'edit':
                section_object_key = ndb.Key(urlsafe=key)
        
                if section_object_key:
                    section_object = section_object_key.get()
                    section_form.populate_obj(section_object)
                    section_object.put()
                    
                    # stored
                    logging.info("(ProviderEducationHandler.post) Stored section %s key=%s" % (section, section_object.key))
                else:
                    logging.info("(ProviderEducationHandler.post) No section object found for key %s" % key)

            # success, empty forms so you can add another one            
            kwargs = self.generate_blank_forms()

            self.render_cv(provider, success_message=saved_message, **kwargs)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit CV: %s %s success" % (operation, section))

        else:            
            kwargs = {}
            for k in self.forms:
                if k == section:
                    # this one has errors
                    kwargs[k + '_form'] = section_form
                else:
                    # blank form
                    kwargs[k + '_form'] = self.forms[k]().get_form()
            
            if operation == 'edit':
                kwargs['edit'] = section
                kwargs['edit_key'] = key
            
            self.render_cv(provider, **kwargs)
            
            # log the event
            self.log_event(user=provider.user, msg="Edit CV: %s %s validation error" % (operation, section))
