import django_reputation.config as config

from django_reputation.models import Permission, Reputation

def reputation(request):
    """
    creates a PERMISSIONS dictionary object in the context 
    which contains keys for eachPermission object defined
    
    PERMISSIONS[action] = True if the current logged in user 
    has permissions to access the action
    
    PERMISSSIONS[action] = False if the current logged in user
    does not have permissions to access the action
    """
    permissions = Permission.objects.all()
    permissions_dict = {}
    
    print request.user.reputation.reputation
    for permission in permissions:
        if getattr(request.user, 'reputation', None):
            permissions_dict[permission.name] = request.user.reputation.reputation >= permission.required_reputation
        else:
            permissions_dict[permission.name] = False
    return {'PERMISSIONS':permissions_dict}