VERSION = (0, 1, None)

from reputation.models import Reputation
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class InitReputation(object):
    def __init__(self):
        post_save.connect(self._post_save_signal_callback, sender = User, weak = False)
    
    def _post_save_signal_callback(self, **kwargs):
        instance = kwargs.get('instance', None)
        created = kwargs.get('created', False)
        if instance and created:
            user_reputation = Reputation.objects.reputation_for_user(instance)
            
init_reputation = InitReputation()
