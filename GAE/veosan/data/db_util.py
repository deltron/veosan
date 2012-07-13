import logging
from google.appengine.ext.ndb import StringProperty, BooleanProperty, TextProperty, IntegerProperty, FloatProperty

def set_all_properties_on_entity_from_multidict(entity, multidict):
    ''' fancy way to set all properties on an entity from a multidict (posted form) '''
    
    for prop in iter(entity.to_dict()):
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
                integer_value = int(multidict.getone(prop))
                setattr(entity, prop, integer_value)

            elif isinstance(property_type, FloatProperty):
                logging.info("saving key->value for Float : " + prop + "->" + multidict.getone(prop))
                integer_value = float(multidict.getone(prop))
                setattr(entity, prop, integer_value)

            elif isinstance(property_type, BooleanProperty):
                logging.info("saving key->value for Boolean : " + prop + "->" + multidict.getone(prop))                
                if multidict.getone(prop) == 'True':
                    setattr(entity, prop, True)
                else:
                    setattr(entity, prop, multidict.getone(prop))          
            else:
                logging.error("Got a property of unknown instance: " + str(property_type))
