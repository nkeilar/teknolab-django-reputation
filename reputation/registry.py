from django.contrib.contenttypes.models import ContentType


class AlreadyRegistered(Exception):
    pass


class ReputationRegistry(object):
    """
    Registry of handler instances in {'app_model': Handler()} format
    """
    def __init__(self):
        self._handlers = {}
    
    def register(self, handler_class):
        """
        Registers a handler instance.
        """
        content_type = ContentType.objects.get_for_model(handler_class.model)
        content_name = "%s_%s" % (content_type.app_label, content_type.model)
        if content_name in self._handlers.keys():
            raise AlreadyRegistered('%s is already registered' % content_name)
        self._handlers[content_name] = handler_class()

reputation_registry = ReputationRegistry()
