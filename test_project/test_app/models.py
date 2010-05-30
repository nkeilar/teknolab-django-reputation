from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from reputation.handlers import BaseReputationHandler


class Link(models.Model):
    link = models.URLField()
    user = models.ForeignKey(User)
    

class Vote(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')
    vote = models.SmallIntegerField(choices=((1, 1), (-1, -1)))
    
    class Meta:
        permissions = (('can_vote_up', 'Can vote up'),
                       ('can_vote_down', 'Can vote down'))


class VotingReputationHandler(BaseReputationHandler):
    model = Vote
    UP_VALUE = 15
    DOWN_VALUE = -5

    def check_conditions(self, instance):
        return True
    
    def get_target_object(self, instance):
        return instance.object
    
    def get_target_user(self, instance):
        return getattr(instance.object, 'user', None)
    
    def get_originating_user(self, instance):
        return getattr(instance, 'user', None)
            
    def get_value(self, instance):
        value = 0
        if instance.vote == 1:
            value = self.UP_VALUE
        elif instance.vote == -1:
            value = self.DOWN_VALUE
        return value

