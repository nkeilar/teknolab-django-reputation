import datetime
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.conf import settings

REPUTATION_MAX_GAIN_PER_DAY = settings.REPUTATION_MAX_GAIN_PER_DAY
REPUTATION_MAX_LOSS_PER_DAY = settings.REPUTATION_MAX_LOSS_PER_DAY

class ReputationManager(models.Manager):
    """
    Custom manager for the "Reputation" model.
    
    Methods defined here provide shortcuts for modifying and tracking the reputation
    of users.
    """
    def reputation_for_user(self, user):
        """
        Returns the "Reputation" object associated with a "User".
        
        if no "Reputation" object currently exists for the user,
        then attempt to create a new "Reputation" object with default
        values.
        """
        try:
            reputation_object = user.reputation
        except ObjectDoesNotExist:
            reputation_object = Reputation(user = user)
            reputation_object.save()
        return reputation_object
    
    def calculate_reputation_for_today(self, user):
        """
        Calculates and returns the total amount of reputation a User 
        has gained today.
        """
        start_time = datetime.datetime.today().replace(hour = 0, minute = 0, second = 0)
        end_time = datetime.datetime.today().replace(hour = 23, minute = 59, second = 59)
        
        relevant_reputation_actions = ReputationAction.objects.filter(user=user,
                                                                      date_created__range = (start_time, end_time))
        # TODO: use Sum() aggregate
        delta = sum([action.value for action in relevant_reputation_actions])
        return delta
    
    def update_reputation(self, user, value):
        """
        Updates an "User"s associated "Reputation" object by adding value to the
        user's current reputation.
        
        if value == 0, then nothing is done.
        """
        if value:
            reputation = self.reputation_for_user(user)
            reputation.reputation = reputation.reputation + value
            reputation.save()
        
    def log_reputation_action(self, user, originating_user, action_value, target_object):
        """
        Attempt to create a ReputationAction object associated with @user
        
        if a ReputationAction is found and uniqueness constraints checking passes,
        then attempt to update @user's reputation.  Checks the current reputation 
        gained today and limits the change in reputation if the user has outbounded
        either REPUTATION_MAX_GAIN_PER_DAY or REPUTATION_MAX_LOSS_PER_DAY.
        """
        content_type_object = ContentType.objects.get_for_model(target_object.__class__)
        object_id = target_object.id
        
        reputation_action = ReputationAction(user = user, 
                                             originating_user = originating_user, 
                                             content_type = content_type_object, 
                                             object_id = object_id,
                                             value = action_value)
        reputation_action.save()
        
        current_delta = Reputation.objects.calculate_reputation_for_today(user)
        expected_delta = action_value + current_delta
        
        if expected_delta <= REPUTATION_MAX_GAIN_PER_DAY and expected_delta >= -1 * REPUTATION_MAX_LOSS_PER_DAY:
            delta = action_value
        elif expected_delta > REPUTATION_MAX_GAIN_PER_DAY:
            delta = REPUTATION_MAX_GAIN_PER_DAY - current_delta
        elif expected_delta < REPUTATION_MAX_LOSS_PER_DAY:
            delta = REPUTATION_MAX_LOSS_PER_DAY - current_delta
        Reputation.objects.update_reputation(user, delta)
    
    def update_user_reputation(self, user, final_value):
        """
        Updates target @user's reputation to @final_value.
        """
        reputation_object = self.reputation_for_user(user)
        reputation_object.reputation = final_value
        reputation_object.save()
        
class Reputation(models.Model):
    """
    Model for storing a "User" object's reputation in an IntegerField.
    """
    reputation = models.IntegerField(default = 0)
    user = models.OneToOneField(User, related_name = 'reputation')
    
    objects = ReputationManager()
    
    def save(self, **kwargs):
        super(Reputation, self).save(**kwargs)
        permissions = []
        for permission, reputation in settings.REPUTATION_PERMISSONS.items():
            if self.reputation > reputation:
                permissions.append(permission)
        self.user.permissions = permissions
    
    def __unicode__(self):
        return "%s - %s" % (str(self.user.username), str(self.reputation))

class ReputationAction(models.Model):
    """
    Model representing an action a user takes that effects the user's reputation.
    """
    user = models.ForeignKey(User, related_name = 'target_user')
    originating_user = models.ForeignKey(User, related_name = 'originating_user')
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    value = models.IntegerField(default = 0)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s - %s" % (str(self.user.username), str(self.action.name))
    
