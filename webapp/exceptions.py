from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

class OccurrenceDoesNotExist(ObjectDoesNotExist):
    ''' The occurrence does not match with event '''
    
    
class MultipleEventReturned(MultipleObjectsReturned):
    ''' One user has more then one event at same time '''

class MultipleSubscriptionReturned(MultipleObjectsReturned):
    ''' One user has more then one event at same time '''
