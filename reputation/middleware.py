import reputation.config as config
from reputation.models import Reputation


class ReputationMiddleware(object):
    """
    middleware for attaching a reputation object to the current logged in user
    if the current user is authenticated (depends on using django.contrib.auth
    or an app that has a similar interface)
    
    If the current logged in user does not have a Reputation object associated,
    then a Reputation object will be created with the base reputation specified
    in the settings.
    
    Depends on request.user being populated with the current logged in user.
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.reputation = Reputation.objects.reputation_for_user(request.user)
        else:
            request.user.reputation = None