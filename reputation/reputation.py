from django_reputation.models import Reputation, ReputationContent
import django_reputation.handlers as handlers
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

class ReputationRegistry(object):
    """
    Registry of handlers for TrackedContent content types.
    """
    def __init__(self):
        self._registry = {}
        self._handlers = {}
        reputation_contents = ReputationContent.objects.all()
        for content in reputation_contents:
            self.register(content.content_type)
    
    def get_handler(self, content_name):
        """
        Returns a handler class based on StudlyCaps notation of
        content_type.app_label + content_type.model + HistoryHandler.
        Defaults to BaseHistoryHandler.
        """
        def to_studly(x):
            return "".join([token.capitalize() for token in x.split("_")])
                            
        handler_class = getattr(handlers, 
                                "%sReputationHandler" % (to_studly(content_name)), 
                                handlers.BaseReputationHandler)
        
        return handler_class
    
    def register(self, content_type):
        """
        Registers a callable handler instance in the registry.
        """
        content_name = "%s_%s" % (content_type.app_label, content_type.model)
        if not content_name in self._registry.keys():
            HandlerClass = self.get_handler(content_name)
            handler = HandlerClass(content_type)
            self._handlers[content_name] = handler
            self._registry[content_name] = content_type
            
reputation_registry = ReputationRegistry()