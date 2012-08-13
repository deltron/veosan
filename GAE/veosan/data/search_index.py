from google.appengine.api import search
import util
import logging

_PROVIDERS_INDEX_NAME = "providers"

def IndexProvider(provider):
    return

    # don't do anything for now
    
    '''
    doc_id = provider.key.urlsafe()
    
    string_fields = (
                     'bio',
                     'quote',
                     'first_name',
                     'last_name',
                     'email',
                     'phone',
                     'address',
                     'city',
                     'postal_code',
                     'province',
                     'vanity_url',
                    )
    
    # append basic text fields
    fields = []
    for field in string_fields:
        fields.append(search.TextField(name=field, value=getattr(provider, field)))
    
    # and the category and specialty
    #fields.append(search.TextField(name='category', value=util.get_all_categories()[provider.category]))
    #fields.append(search.TextField(name='specialty', value=util.getAllSpecialities()[provider.specialty]))

    document = search.Document(doc_id, fields)

    try:
        search.Index(name=_PROVIDERS_INDEX_NAME).add(document)
    except search.Error:
        logging.info("Add provider to search index failed")
'''



