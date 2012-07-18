import logging
from google.appengine.ext.ndb import StringProperty, BooleanProperty, TextProperty, IntegerProperty, FloatProperty

def set_all_properties_on_entity_from_multidict(entity, multidict, form):
    ''' fancy way to set all properties on an entity from a multidict (posted form) '''
    field_list = []
    for field in form:
        field_list.append(field.name)
            
    for prop in iter(entity.to_dict()):
        # check if it's in the form
        if prop in field_list:
            
            # check if it's in the request, if yes set it
            if multidict.has_key(prop):
                property_type = entity._properties[prop]
    
                if isinstance(property_type, StringProperty):
                    if property_type._repeated:
                        logging.info("saving key->value for String List : " + prop + "->" + str(multidict.getall(prop)))
                        setattr(entity, prop, multidict.getall(prop))    
                    else:
                        logging.info("saving key->value for String : " + prop + "->" + multidict.getone(prop))
                        setattr(entity, prop, multidict.getone(prop))
    
                elif isinstance(property_type, TextProperty):
                    logging.info("saving key->value for Text : " + prop + "->" + multidict.getone(prop))
                    setattr(entity, prop, multidict.getone(prop))
    
                elif isinstance(property_type, IntegerProperty):
                    logging.info("saving key->value for Integer : " + prop + "->" + multidict.getone(prop))
                    if multidict.getone(prop):
                        integer_value = int(multidict.getone(prop))
                        setattr(entity, prop, integer_value)
    
                elif isinstance(property_type, FloatProperty):
                    logging.info("saving key->value for Float : " + prop + "->" + multidict.getone(prop))
                    if multidict.getone(prop):
                        float_value = float(multidict.getone(prop))
                        setattr(entity, prop, float_value)
    
                elif isinstance(property_type, BooleanProperty):
                    logging.info("saving key->value for Boolean : " + prop + "->" + multidict.getone(prop))                
                    if multidict.getone(prop) == 'True':
                        setattr(entity, prop, True)
                    else:
                        setattr(entity, prop, multidict.getone(prop))          
                else:
                    logging.error("Got a property of unknown instance: " + str(property_type))
            
            else:
                # there's a field in the form with no value, unset it on the entity
                property_type = entity._properties[prop]
                if property_type._repeated:
                    setattr(entity, prop, [])
                else:
                    setattr(entity, prop, None)

