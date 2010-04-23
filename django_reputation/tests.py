import unittest

from django.contrib.auth.models import User
from django_reputation.models import (Reputation, ReputationAction, UserReputationAction,
                                      Permission, ReputationContent)
import django_reputation.config as config
from django_reputation.decorators import ReputationRequired, reputation_required
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

class DummyRequest(object):
    def __init__(self):
        self.user = User(username = 'Test Request User')
        self.user.save()
        Reputation.objects.reputation_for_user(self.user)
        
class DummyDecClass(object):
    def __init__(self):
        pass
    
    def call(self, request):
        return 'YO'
    __call__ = ReputationRequired(call, 'test permission')
    
class ReputationDecoratorTests(unittest.TestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username = 'Test User',
                                          email = 'test_user@gmail.com')
        self.user_1 = user_1
        
        user_2 = User.objects.create_user(username = 'Test User 2',
                                          email = 'test_user2@gmail.com')
        self.user_2 = user_2
        Reputation.objects.reputation_for_user(self.user_1)
        Reputation.objects.reputation_for_user(self.user_2)

        Reputation.objects.update_user_reputation(self.user_1, 5000)
        
        test_permission, created = Permission.objects.get_or_create(name = 'test permission',
                                                           description = '',
                                                           required_reputation = 4500)
        self.test_permission = test_permission
        
        request = DummyRequest()
        self.request = request
        
    def tearDown(self):
        self.user_1.delete()
        self.user_2.delete()
        self.test_permission.delete()
        
    def test_reputation_required(self):
        """
        Tests ReputationRequired decorator.
        """
        Reputation.objects.update_user_reputation(self.user_1, 5000)
        dummy_class = DummyDecClass()
        status = dummy_class(self.request)
        self.assertEqual(status, 'YO')
        
        Reputation.objects.update_user_reputation(self.user_1, 2000)
        self.request.user = self.user_1
        dummy_class = DummyDecClass()
        status = dummy_class(self.request)
        self.assertEqual(status.__class__, http.HttpResponseRedirect)
    
class ReputationRegistrationTests(unittest.TestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username = 'Test User',
                                          email = 'test_user@gmail.com')
        self.user_1 = user_1
        
        user_2 = User.objects.create_user(username = 'Test User 2',
                                          email = 'test_user2@gmail.com')
        self.user_2 = user_2
        Reputation.objects.reputation_for_user(self.user_1)
        Reputation.objects.reputation_for_user(self.user_2)
        
        user_reputation_content, created = ReputationContent.objects.get_or_create(content_type = ContentType.objects.get_for_model(User))
        self.user_reputation_content = user_reputation_content
    
    def tearDown(self):
        self.user_1.delete()
        self.user_2.delete()
        self.user_reputation_content.delete()
        
    def test_handler_registration(self):
        """
        Tests registration of handlers for reputation post_save signals.
        """
        import django_reputation.handlers as handlers
        from django_reputation.reputation import reputation_registry, ReputationRegistry
        
        reputation_registry = ReputationRegistry()
        user_content_name = "%s_%s" % (self.user_reputation_content.content_type.app_label, 
                                       self.user_reputation_content.content_type.model)
        self.assertEqual(reputation_registry._handlers.get(user_content_name).__class__, handlers.BaseReputationHandler)