import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist

from django_reputation.models import Permission
from django_reputation.config import REPUTATION_REQUIRED_TEMPLATE

def reputation_required(request,  permission_name):
    """
    Redirect to this view when an user fails a reputation check for accessing content
    on the site.
    """
    try:
        permission = Permission.objects.get(name = permission_name)
    except ObjectDoesNotExist:
        permission = None
    
    return shortcuts.render_to_response(REPUTATION_REQUIRED_TEMPLATE,  
                                        {'permission':permission},  
                                        context_instance = RequestContext(request))
