import logging

def set_all_properties_on_entity_from_multidict(entity, multidict):
    ''' fancy way to set all properties on an entity from a multidict (posted form) '''
    
    for prop in iter(entity.properties()):
        if multidict.has_key(prop):
            property_data_type = entity.properties()[prop].data_type

            if property_data_type == basestring:
                logging.info("saving key->value for string : " + prop + "->" + multidict.getone(prop))
                setattr(entity, prop, multidict.getone(prop))
            elif property_data_type == list:
                logging.info("saving key->value for list :" + prop + " -> " + str(multidict.getall(prop)))
                setattr(entity, prop, multidict.getall(prop))
            elif property_data_type == bool:
                logging.info("saving key->value for bool : " + prop + "->" + multidict.getone(prop))                
                if multidict.getone(prop) == 'True':
                    setattr(entity, prop, True)
                else:
                    setattr(entity, prop, multidict.getone(prop))          
            else:
                logging.error("Got a property of unknown instance: " + str(property_data_type))
