from google.appengine.ext import ndb

class Invite(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)

    provider = ndb.KeyProperty(kind='Provider')
    token = ndb.StringProperty()
    link_clicked = ndb.BooleanProperty(default=False)
    profile_created = ndb.BooleanProperty(default=False)

    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    note = ndb.TextProperty()


class ProviderNetworkConnection(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    
    invite = ndb.KeyProperty(kind='Invite')

    source_provider = ndb.KeyProperty(kind='Provider')
    target_provider = ndb.KeyProperty(kind='Provider')
    relationship = ndb.StringProperty()
    confirmed = ndb.BooleanProperty(default=False)
    rejected = ndb.BooleanProperty(default=False)
    rejection_count = ndb.IntegerProperty(default=0)

    
    def _pre_put_hook(self):
        # don't connect with yourself
        if self.source_provider == self.target_provider:
            raise Exception('Invalid connection to self')
                
        # remove any dupes from the network graph
        
        # check for duplicate source->target
        source_target_count = ProviderNetworkConnection.query(
                            ProviderNetworkConnection.source_provider == self.source_provider,
                            ProviderNetworkConnection.target_provider == self.target_provider,
                            ProviderNetworkConnection.confirmed == True,
                            ).count()
        
        if source_target_count > 0:
            raise Exception('Duplicate source to target')

        # check for duplicate target->source
        source_target_count = ProviderNetworkConnection.query(
                            ProviderNetworkConnection.target_provider == self.source_provider,
                            ProviderNetworkConnection.source_provider == self.target_provider, 
                            ProviderNetworkConnection.confirmed == True,
                            ).count()
        
        if source_target_count > 0:
            raise Exception('Duplicate target to source')


class PatientNetworkConnection(ndb.Model):
    created_on = ndb.DateTimeProperty(auto_now_add=True)

    source_provider = ndb.KeyProperty(kind='Provider')
    target_patient = ndb.KeyProperty(kind='Patient')
    relationship = ndb.StringProperty()
    status = ndb.StringProperty()

