from reputation.models import ReputationAction, Reputation
from django.db.models.signals import post_save, post_delete


class BaseReputationHandler(object):
    """
    Default handler for creating AppModelReputationHandler objects.
    """
    
    def __init__(self, content_type_object):
        self.content_type_object = content_type_object
        self.model = content_type_object.model_class()
        self._connect_signals()
        
    def _connect_signals(self):
        post_save.connect(self._post_save_signal_callback, sender=self.model, weak = False)
            
    def _post_save_signal_callback(self, **kwargs):
        instance = kwargs['instance']
        created = kwargs['created']
        if created:
            self.modify_reputation(instance)
    
    def check_conditions(self, instance):
        return False
    
    def get_target_object(self, instance):
        pass
    
    def get_target_user(self, instance):
        pass
    
    def get_originating_user(self, instance):
        pass
    
    def get_reputation_action(self, instance):
        pass
    
    def get_value(self, instance):
        return 0
    
    def modify_reputation(self, instance):
        if self.check_conditions(instance):
            target_user = self.get_target_user(instance)
            originating_user = self.get_originating_user(instance)
            action = self.get_reputation_action(instance)
            target_object = self.get_target_object(instance)
            value = self.get_value(instance)
            reputation_action_object = Reputation.objects.log_reputation_action(user = target_user, 
                                                                                originating_user = originating_user,
                                                                                action_name = action.name,
                                                                                target_object = target_object,
                                                                                action_value = value)
        
    