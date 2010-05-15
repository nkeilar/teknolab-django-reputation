import datetime

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from django_reputation.exceptions import ReputationException
from django_reputation.config import (MAX_REPUTATION_GAIN_PER_DAY, 
                                      MAX_REPUTATION_LOSS_PER_DAY, 
                                      BASE_REPUTATION)

class ReputationManager(models.Manager):
    """
    Custom manager for the "Reputation" model.
    
    Methods defined here provide shortcuts for modifying and tracking the reputation
    of users.
    """
    def reputation_for_user(self, user):
        """
        Returns the "Reputation" object associated with an "User".
        
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
        Calculates and returns the total amount of reputation an "User" 
        has gained today.
        """
        start_time = datetime.datetime.today().replace(hour = 0, minute = 0, second = 0)
        end_time = datetime.datetime.today().replace(hour = 23, minute = 59, second = 59)
        
        relevant_reputation_actions = UserReputationAction.objects.filter(date_created__range = (start_time, end_time))
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
        
    def log_reputation_action(self, user, originating_user, action_name, action_value, target_object):
        """
        Attempt to create an "UserReputationAction" object associated with @user,
        @object and a "ReputationAction" object with name @action_name.
        
        checks uniqueness constraints on the "ReputationAction" object if found.
        
        if an "ReputationAction" is found and uniqueness constraints checking passes,
        then attempt to update @user's reputation.  Checks the current reputation 
        gained today and limits the change in reputation if the user has outbounded
        either MAX_REPUTATION_GAIN_PER_DAY or MAX_REPUTATION_LOSS_PER_DAY.
        """
        content_type_object = ContentType.objects.get_for_model(target_object.__class__)
        object_id = target_object.id
        
        try:
            action = ReputationAction.objects.get(name = action_name)
        except ObjectDoesNotExist:
            raise ReputationException('No reputation action named %s available for %s'
                                          % (action_name, content_type.model))
                             
        user_reputation_action = UserReputationAction(user = user, 
                                                      originating_user = originating_user, 
                                                      action = action, 
                                                      content_type = content_type_object, 
                                                      object_id = object_id,
                                                      value = action_value)
        user_reputation_action.save()
        
        current_delta = Reputation.objects.calculate_reputation_for_today(user)
        expected_delta = action_value + current_delta
        
        if expected_delta <= MAX_REPUTATION_GAIN_PER_DAY and expected_delta >= -1 * MAX_REPUTATION_LOSS_PER_DAY:
            delta = action_value
        elif expected_delta > MAX_REPUTATION_GAIN_PER_DAY:
            delta = MAX_REPUTATION_GAIN_PER_DAY - current_delta
        elif expected_delta < MAX_REPUTATION_LOSS_PER_DAY:
            delta = MAX_REPUTATION_LOSS_PER_DAY - current_delta
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
    reputation = models.IntegerField(default = BASE_REPUTATION)
    user = models.OneToOneField(User, related_name = 'reputation')
    
    objects = ReputationManager()
    
    def __unicode__(self):
        return "%s - %s" % (str(self.user.username), str(self.reputation))

class ReputationContent(models.Model):
    """
    Content types that induce changes in user reputations when modified.
    """
    content_type = models.ForeignKey(ContentType)
    
    def __unicode__(self):
        return self.content_type.model
    
class ReputationAction(models.Model):
    """
    Model representing a type of user action that can impact another user's reputation.
    
    all ReputationActions instances are associated with a ContentType, so 
    ReputationActions of the same name can be specified for differing ContenTypes.
    
    The field unique_for_content if true only allows one "UserReputationAction" object
    to be created per user for each ContentType.
    
    The field unique_for_object if true only allows one "UserReputationAction" object
    to be created per user for each object. 
    """
    name = models.CharField(max_length = 75)
    description = models.TextField(default = '')
        
    def __unicode__(self):
        return self.name
        
class UserReputationAction(models.Model):
    """
    Model representing an action an user takes that effects the user's reputation.
    An 'instance' of a ReputationAction.
    """
    action = models.ForeignKey(ReputationAction)
    user = models.ForeignKey(User, related_name = 'target_user')
    originating_user = models.ForeignKey(User, related_name = 'originating_user')
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    value = models.IntegerField(default = 0)
    date_created = CreationDateTimeField()
    
    def __unicode__(self):
        return "%s - %s" % (str(self.user.username), str(self.action.name))
    
class Permission(models.Model):
    """
    Model representing the required reputation needed to perform an action on the site.
    """
    name = models.CharField(max_length = 75, unique = True)
    description = models.TextField(default = '')
    required_reputation = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return "%s - %s" % (str(self.name), str(self.required_reputation))