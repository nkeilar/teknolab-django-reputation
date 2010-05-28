from reputation.models import Reputation
from reputation.handlers import BaseReputationHandler


class AlreadyRegistered(Exception):
    pass


class ReputationRegistry(object):
    """
    Registry of handlers.
    """
    def __init__(self):
        self._handlers = {}
    
    def get_handler(self, content_name):
        """
        Returns a handler class based on content_name.
        Defaults to BaseReputationHandler.
        """
        return self._handlers.get('content_name', BaseReputationHandler)
    
    def register(self, handler_instance):
        """
        Registers a handler instance.
        """
        if model in self._registry:
            raise AlreadyRegistered('The model %s is already registered' % model.__name__)
        content_name = "%s_%s" % (content_type.app_label, content_type.model)
        self._registry[content_name] = handler_instance

reputation_registry = ReputationRegistry()
