import unittest

from django.contrib.auth.models import User
from reputation.models import Reputation, ReputationAction, UserReputationAction
import reputation.config as config
from reputation.decorators import ReputationRequired, reputation_required
import django.http as http
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

class Tests(unittest.TestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username = 'Test User',
                                          email = 'test_user@gmail.com')
        self.user_1 = user_1
        
        user_2 = User.objects.create_user(username = 'Test User 2',
                                          email = 'test_user2@gmail.com')
        self.user_2 = user_2
        
        reputation_action, created = ReputationAction.objects.get_or_create(name = 'vote', description = '')
        self.reputation_action = reputation_action
        
    def tearDown(self):
        self.user_1.delete()
        self.user_2.delete()
        self.reputation_action.delete()
        for reputation in Reputation.objects.all():
            reputation.delete()
        for action in UserReputationAction.objects.all():
            action.delete()
        
    def test_reputation_for_user(self):
        """
        Tests retrieval of the reputation associated with a user.
        """
        reputation_object = Reputation.objects.reputation_for_user(self.user_1)
        self.assertTrue(reputation_object)
        self.assertEqual(reputation_object.reputation, config.BASE_REPUTATION)
    
    def test_log_reputation_action(self):
        """
        Tests creating a new UserReputationAction.
        """
        Reputation.objects.log_reputation_action(user = self.user_1,
                                                 originating_user = self.user_2,
                                                 action_name = 'vote',
                                                 action_value = 100,
                                                 target_object = self.user_1)
        reputation_object = Reputation.objects.reputation_for_user(self.user_1)
        self.assertEqual(reputation_object.reputation, 100 + config.BASE_REPUTATION)
        
        reputation_actions = UserReputationAction.objects.all()
        self.assertTrue(reputation_actions)
        self.assertEqual(reputation_actions[0].action, self.reputation_action)
    
    def test_calculate_reputation_for_today(self):
        """
        Tests calculation of total reputation gain in a day.
        """
        Reputation.objects.log_reputation_action(user = self.user_1,
                                                 originating_user = self.user_2,
                                                 action_name = 'vote',
                                                 action_value = 100,
                                                 target_object = self.user_1)
        delta = Reputation.objects.calculate_reputation_for_today(self.user_1)
        self.assertEqual(delta, 100)
